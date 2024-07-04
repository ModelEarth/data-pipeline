import duckdb
import os
import pandas as pd
from tqdm import tqdm
import os
import math
import csv


class DuckDBManager:
    def __init__(self, db_path='database/us_economic_data.duckdb', export_dir='database/exported_tables'):
        self.db_path = db_path
        self.export_dir = export_dir
        self.conn = None  # Placeholder for the database connection
        self._connect_db()

    def _connect_db(self):
        """Establishes a database connection."""
        if not os.path.exists(self.db_path):
            print(f"Database {self.db_path} does not exist. Creating new database...")
        self.conn = duckdb.connect(self.db_path)
        self._create_tables()

    def _close_db(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def _create_tables(self):
        if self.conn:
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



    def export_to_csv(self):
        os.makedirs(self.export_dir, exist_ok=True)
        
        self.conn.execute(f"COPY (SELECT * FROM DimNaics) TO '{self.export_dir}/DimNaics.csv' WITH (FORMAT CSV, HEADER TRUE)")
        self.conn.execute(f"COPY (SELECT * FROM DimZipCode) TO '{self.export_dir}/DimZipCode.csv' WITH (FORMAT CSV, HEADER TRUE)")
        self.conn.execute(f"COPY (SELECT * FROM DimYear) TO '{self.export_dir}/DimYear.csv' WITH (FORMAT CSV, HEADER TRUE)")

        # Get the list of valid years from DimYear
        valid_years = self.conn.execute("SELECT Year FROM DimYear").fetchall()
        # Define the known industry levels
        industry_levels = [2, 4, 6]
        
        # Define maximum file size in bytes (25MB)
        max_file_size = 25 * 1024 * 1024

        # Loop through each valid year and industry level to export the corresponding DataEntry data
        for year_tuple in tqdm(valid_years, desc="Exporting DataEntry CSV files"):
            year = year_tuple[0]  # Extract the year from the tuple
            for industry_level in industry_levels:
                # Get the total number of rows for the current year and industry level
                total_rows_query = f"""
                SELECT COUNT(*) FROM DataEntry
                WHERE Year = {year} AND IndustryLevel = {industry_level}
                """
                total_rows = self.conn.execute(total_rows_query).fetchone()[0]

                if total_rows == 0:
                    continue

                # Estimate the number of chunks based on the average row size
                avg_row_size_query = f"""
                SELECT AVG(LENGTH(CAST(EntryID AS VARCHAR)) + 
                        LENGTH(CAST(GeoID AS VARCHAR)) + 
                        LENGTH(CAST(NaicsCode AS VARCHAR)) + 
                        LENGTH(CAST(Year AS VARCHAR)) + 
                        LENGTH(CAST(Establishments AS VARCHAR)) + 
                        LENGTH(CAST(Employees AS VARCHAR)) + 
                        LENGTH(CAST(Payroll AS VARCHAR)) + 
                        LENGTH(CAST(IndustryLevel AS VARCHAR))) 
                FROM DataEntry
                WHERE Year = {year} AND IndustryLevel = {industry_level}
                """
                avg_row_size = self.conn.execute(avg_row_size_query).fetchone()[0]

                # If avg_row_size is None, use a default size (e.g., 500 bytes)
                if avg_row_size is None:
                    avg_row_size = 500

                rows_per_chunk = math.ceil(max_file_size / avg_row_size)

                # Export data in chunks
                for start in range(0, total_rows, rows_per_chunk):
                    chunk_file_path = f'{self.export_dir}/DataEntry_{year}_IndustryLevel_{industry_level}_chunk_{start // rows_per_chunk}.csv'
                    
                    # Execute the query and export the data
                    query = f"""
                    COPY (
                        SELECT * 
                        FROM DataEntry
                        WHERE Year = {year} AND IndustryLevel = {industry_level}
                        LIMIT {rows_per_chunk} OFFSET {start}
                    ) TO '{chunk_file_path}' WITH (FORMAT CSV, HEADER TRUE)
                    """
                    self.conn.execute(query)




    def import_csv_files(self, table_name):
        
        csv_files = [f for f in os.listdir(self.export_dir) if f.endswith('.csv') and f.startswith(table_name)]
        if not csv_files:
            print(f"No CSV files found with prefix {table_name}.")
            self._close_db()
            return
        
        for csv_file in tqdm(csv_files, desc=f"Importing {table_name} CSV file(s)"):
            csv_file_path = os.path.join(self.export_dir, csv_file)
            self.conn.execute(f'''
            INSERT INTO {table_name}
            SELECT * FROM read_csv_auto('{csv_file_path}')
            ''')



    def check_row_length(self, tablename):
        
        query = f"SELECT COUNT(*) FROM {tablename}"
        result = self.conn.execute(query).fetchone()
        
        return result[0]

    def import_all_csv_files(self):
        self._create_tables()

        self.import_csv_files('DataEntry')
        self.import_csv_files('DimNaics')
        self.import_csv_files('DimYear')
        self.import_csv_files('DimZipCode')


    def get_schema(self):

        schema = {}
        tables = self.conn.execute("SHOW TABLES").fetchall()

        for table in tables:
            table_name = table[0]
            columns = self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            schema[table_name] = [(col[1], col[2]) for col in columns]  # (column_name, data_type)

        return schema


    def execute_query(self, query):
        
        result = self.conn.execute(query)
        df = result.fetchdf()
        
        return df
    
    def filter_by_year_zip_industry(self, year, zip_prefix, industry_level):
        if zip_prefix > 9:
            raise ValueError("The zip prefix must be single digit")
        query = f"""
            SELECT * FROM DataEntry
            WHERE Year = {year}
            AND SUBSTR(GeoID, 1, 1) = '{zip_prefix}'
            AND IndustryLevel = {industry_level}
        """
        return self.execute_query(query)

    def filter_by_industry_level(self, industry_level):
        query = f"""
            SELECT * FROM DataEntry
            WHERE IndustryLevel = {industry_level}
        """
        return self.execute_query(query)
    

    def filter_by_zip_prefix(self, zip_prefix):
        if zip_prefix > 9:
            raise ValueError("The zip prefix must be single digit")
        
        query = f"""
            SELECT * FROM DataEntry
            WHERE SUBSTR(GeoID, 1, 3) = '{zip_prefix}'
        """
        return self.execute_query(query)

    def filter_by_year(self, year):
        query = f"""
        SELECT * FROM DataEntry
        WHERE Year = {year}
        """
        return self.execute_query(query)

    def check_database_exists(self):
        return os.path.exists(self.db_path)

    def check_csv_files_exist(self, prefix):
        csv_files = [f for f in os.listdir(self.export_dir) if f.endswith('.csv') and f.startswith(prefix)]
        return bool(csv_files)


    def export_geo_nested_csv(self):
        """Exports data entries to nested directories based on GeoID, skips if file exists."""
        base_dir = os.path.join(self.export_dir, "nested_zip")
        os.makedirs(base_dir, exist_ok=True)

        geo_ids = self.conn.execute("SELECT DISTINCT GeoID FROM DataEntry").fetchall()
        for (geo_id,) in tqdm(geo_ids, desc="Processing GeoIDs"):
            path_components = [base_dir] + list(geo_id)
            geo_path = os.path.join(*path_components)
            os.makedirs(geo_path, exist_ok=True)

            combinations = self.conn.execute(f"""
                SELECT DISTINCT Year, IndustryLevel FROM DataEntry WHERE GeoID = '{geo_id}'
            """).fetchall()

            for year, industry_level in combinations:
                chunk_file_path = os.path.join(geo_path, f"data_{year}_{industry_level}.csv")
                # Check if the file already exists
                if os.path.exists(chunk_file_path):
                    print(f"Skipping existing file: {chunk_file_path}")
                    continue
                query = f"""
                COPY (
                    SELECT * FROM DataEntry WHERE GeoID = '{geo_id}' AND Year = {year} AND IndustryLevel = {industry_level}
                ) TO '{chunk_file_path}' WITH (FORMAT CSV, HEADER TRUE)
                """
                self.conn.execute(query)


    def close(self):
        if self.conn:
            self.conn.close()
