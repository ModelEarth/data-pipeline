import duckdb
import pandas as pd
import requests as r
import re
from tqdm import tqdm
import datetime
import os

class DatabasePopulator:
    def __init__(self, db_path='../zip_data/duck_db_manager/database/us_economic_data.duckdb', startyear=2012, endyear=None):
        self.db_path = db_path
        self.conn = None
        self.startyear = startyear
        self.endyear = endyear if endyear else datetime.datetime.now().year - 1

    def __enter__(self):
        self.conn = duckdb.connect(self.db_path)
        self._create_tables()
        self.populate_dim_zipcode()
        self.populate_naics()
        self.populate_year()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def open(self):
        if not self.conn:
            self.conn = duckdb.connect(self.db_path)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def generate_entry_ids(self, num_rows):
        next_ids = self.conn.execute(f"SELECT nextval('entryid_seq') FROM range(0, {num_rows})").fetchall()
        return [row[0] for row in next_ids]

    def insert_data_entries(self, data_rows):
        try:
            num_rows = len(data_rows)
            entry_ids = self.generate_entry_ids(num_rows)

            data_rows_with_id = [
                (entry_id,) + tuple(row)
                for entry_id, row in zip(entry_ids, data_rows)
            ]

            columns = ['EntryID', 'GeoID', 'NaicsCode', 'Year', 'Establishments', 'Employees', 'Payroll', 'IndustryLevel']
            df = pd.DataFrame(data_rows_with_id, columns=columns)

            df.to_csv('../temp/data_entries_temp.csv', index=False)

            self.conn.execute("COPY DataEntry FROM '../temp/data_entries_temp.csv' (AUTO_DETECT TRUE)")

        except duckdb.Error as e:
            print(f"An error occurred: {e}")

    def data_for_year_and_sector_exists(self, year, sector):
        query = '''
            SELECT EXISTS(
                SELECT 1 FROM DataEntry WHERE Year = ? AND NaicsCode = ?
            )
        '''
        result = self.conn.execute(query, (year, sector)).fetchone()
        return result[0] == 1 if result else False

    def data_exists(self, table_name):
        query = f"SELECT EXISTS(SELECT 1 FROM {table_name} LIMIT 1)"
        result = self.conn.execute(query).fetchone()
        return result[0] == 1 if result else False

    def _create_tables(self):
        try:
            self.conn.execute("CREATE SEQUENCE entryid_seq")
        except duckdb.CatalogException:
            pass
        temp_dir = '../temp'

        # Check if the directory already exists
        if not os.path.exists(temp_dir):
            # Create the directory
            os.makedirs(temp_dir)
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS DimZipCode (
                GeoID VARCHAR,
                City TEXT,
                State TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS DimNaics (
                NaicsCode VARCHAR,
                industry_detail TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS DimYear (
                Year INTEGER,
                YearDescription TEXT
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS DataEntry (
                EntryID INTEGER,
                GeoID VARCHAR,
                NaicsCode VARCHAR,
                Year INTEGER,
                Establishments INTEGER,
                Employees INTEGER,
                Payroll INTEGER,
                IndustryLevel INT
            )
        ''')
    

    def get_all_zipcode_names(self, year):
        url = f"https://api.census.gov/data/{year}/zbp?get=GEO_TTL&for=zip%20code:*&key=975f39a54e48438ceebf303d6018e34db212e804"
        if int(year) == 2017 or int(year) == 2018:
            url = f"https://api.census.gov/data/{year}/zbp?get=NAME&for=zip%20code:*&key=975f39a54e48438ceebf303d6018e34db212e804"
        if int(year) > 2018:
            url = f"https://api.census.gov/data/{year}/cbp?get=NAME&for=zip%20code:*&key=975f39a54e48438ceebf303d6018e34db212e804"
        
        response = r.get(url)
        if response.status_code == 200:
            data = response.json()
            return [(row[1], row[0]) for row in data[1:]]
        else:
            #print(f"Failed to fetch data for year {year}: {response.status_code}")
            return []

    def extract_city_state(self, geo_name):
        match = re.match(r'ZIP \d+ \((.+), (.+)\)', geo_name)
        if match:
            return match.group(1), match.group(2)
        else:
            return None, None

    def populate_dim_zipcode(self):
        if self.data_exists('DimZipCode'):
            return
        
        unique_zip_code_data = set()
        for year in tqdm(range(2012, datetime.datetime.now().year - 1), desc="Fetching zip code names"):
            zip_code_data = self.get_all_zipcode_names(str(year))
            for geo_id, geo_name in zip_code_data:
                city, state = self.extract_city_state(geo_name)
                if city and state:
                    unique_zip_code_data.add((geo_id, city, state))

        columns = ['GeoID', 'City', 'State']
        df = pd.DataFrame(list(unique_zip_code_data), columns=columns)

        df.to_csv('../temp/zip_code_temp.csv', index=False)
        self.conn.execute("COPY DimZipCode FROM '../temp/zip_code_temp.csv' (AUTO_DETECT TRUE)")

        sql = """
            INSERT INTO DimZipCode (GeoID, City, State)
            VALUES (?, ?, ?)
        """
        self.conn.execute(sql, ['99999', None, None])

    def populate_naics(self):
        if self.data_exists('DimNaics'):
            return
        df = pd.read_csv('id_lists/industry_id_list.csv')

        def format_naics(value):
            if value == 0.0:
                return '00'
            else:
                return str(int(value)).zfill(2)

        df['relevant_naics'] = df['relevant_naics'].apply(format_naics)

        for _, row in tqdm(df.iterrows(), desc="Fetching NAICS"):
            self.conn.execute('INSERT INTO DimNaics (NaicsCode, industry_detail) VALUES (?, ?)', (row['relevant_naics'], row['industry_detail']))

    def populate_year(self):  
        if self.data_exists('DimYear'):
            return
        
        def _naics_year_selector(year):
            if year >= 2000 and year <= 2002:
                return "NAICS1997"
            elif year >= 2003 and year <= 2007:
                return "NAICS2002"
            elif year >= 2008 and year <= 2011:
                return "NAICS2007"
            elif year >= 2012 and year <= 2016:
                return "NAICS2012"
            return "NAICS2017"

        years_data = [(year, _naics_year_selector(year)) for year in tqdm(range(self.startyear, self.endyear + 1), desc="Fetching years")]

        self.conn.executemany('INSERT INTO DimYear (Year, YearDescription) VALUES (?, ?)', years_data)
