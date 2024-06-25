import datetime
import requests as r
import time
import database_populator as dbp
import pandas as pd
from tqdm import tqdm

class ZipPopulator:
    def __init__(self, startyear=2012, endyear=None, api_headers=None):
        self.api_headers = api_headers
        self.base_url = "https://api.census.gov/data"
        self.startyear = startyear
        self.endyear = endyear if endyear else datetime.datetime.now().year - 1
        with dbp.DatabasePopulator(startyear=self.startyear, endyear=self.endyear) as db_populator:
            self.db_populator = db_populator
        
        self.failed_attempts = set()


    def get_zip_for_year(self, year):
        industries = pd.read_csv('./id_lists/industry_id_list.csv')
        industries['relevant_naics'] = industries['relevant_naics'].astype(int).astype(str)
        industries['level'] = industries['relevant_naics'].apply(len)
        industries = industries[industries['level'].isin([2, 4, 6])]
        if not hasattr(industries, 'get') or 'relevant_naics' not in industries:
            raise ValueError("industries must be a dictionary-like object with a 'relevant_naics' key")

        self.db_populator.open()
        for industry in tqdm(industries['relevant_naics'], desc=f"Inserting for year: {year}"):
            self._get_zip_and_year_help(industry, year)
        self.db_populator.close()
 

    def _get_zip_and_year_help(self, industry, year):
        if (industry, year) in self.failed_attempts:
            #print(f"Skipping industry data for industry: {industry} year: {year} due to previous failure")
            return

        #print(f"Getting industry data for industry: {industry}\tyear: {year}")
        data, status_code = self._get_response_data(industry, year)
        if status_code == 304:
            return

        if status_code == 204 or status_code != 200:
            #print(f"Failed to fetch data for year {year}: {status_code}")
            self.failed_attempts.add((industry, year))
            return

        data_excluding_column_names = data[1:]
        batch_data = []

        for line in data_excluding_column_names:
            naics_code = str(line[1]).strip()
            row = self._create_row(naics_code, line, year)
            batch_data.append(row)

            if len(batch_data) >= 1000:
                self.db_populator.insert_data_entries(batch_data)
                batch_data = []

        if batch_data:
            self.db_populator.insert_data_entries(batch_data)

        #print(f"Finished processing {industry} for {year}.")

    def get_zip_zbp(self, industry):
        years = range(self.startyear, self.endyear + 1)
        for year in years:
            self._get_zip_and_year_help(industry, year)

    def get_all_zip_zbp(self):
        industries = pd.read_csv('./id_lists/industry_id_list.csv')
        industries['relevant_naics'] = industries['relevant_naics'].astype(int).astype(str)
        industries['level'] = industries['relevant_naics'].apply(len)
        industries = industries[industries['level'].isin([2, 4, 6])]
        if not hasattr(industries, 'get') or 'relevant_naics' not in industries:
            raise ValueError("industries must be a dictionary-like object with a 'relevant_naics' key")

        self.db_populator.open()

        for industry in industries['relevant_naics']:
            if industry == 0:
                self.get_zip_zbp('00')
            else:
                self.get_zip_zbp(industry)

        self.db_populator.close()

    def _escape_and_quote(self, item):
        if item is None or item == '':
            return '"0"'
        escaped_item = item.replace('"', '""')
        return f'"{escaped_item}"'

    def _naics_year_selector(self, year):
        if year >= 2000 and year <= 2002:
            return "NAICS1997"
        elif year >= 2003 and year <= 2007:
            return "NAICS2002"
        elif year >= 2008 and year <= 2011:
            return "NAICS2007"
        elif year >= 2012 and year <= 2016:
            return "NAICS2012"
        return "NAICS2017"

    def _valid_naics_level(self, naics_code):
        if '-' in naics_code:
            parts = naics_code.split('-')
            if all(part.isdigit() for part in parts):
                return len(parts[0])
        return len(naics_code)

    def _create_row(self, naics_code, line, year):
        return [
            line[0],  # GeoID
            naics_code,
            year,
            line[2],  # Establishments
            line[3],  # Employees
            line[4],  # Payroll
            len(naics_code)
        ]

    def _get_response_data(self, sector, year, attempt=1):
        if self.db_populator.data_for_year_and_sector_exists(year, sector):
            #print(f"Data for sector {sector} and year {year} already exists in the database. Skipping API call.")
            return {}, 304

        code = self._naics_year_selector(year)
        if not isinstance(sector, str):
            sector = str(sector)
        if sector == '0':
            sector = '00'
        url = f"{self.base_url}/{year}/zbp?get=ZIPCODE,{code},ESTAB,EMP,PAYANN&for=zip%20code:*&{code}={sector}&key={self.api_headers['x-api-key']}"

        if year > 2018:
            url = f"{self.base_url}/{year}/cbp?get=ZIPCODE,{code},ESTAB,EMP,PAYANN&for=zip%20code:*&{code}={sector}&key={self.api_headers['x-api-key']}"
        response = r.get(url, headers=self.api_headers)

        if response.status_code == 429:
            if attempt <= 5:
                sleep_time = (2 ** attempt)
                print(f"Rate limit exceeded, retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                return self._get_response_data(sector, year, attempt + 1)
            else:
                print("Max retry attempts reached, unable to retrieve data.")
                return {}, 429

        if response.status_code == 200:
            data = response.json()
            return data, 200
        else:
            #print(f"Failed to fetch data: {response.status_code}")
            return {}, response.status_code

    def close_resources(self):
        if self.db_populator:
            self.db_populator.close()
