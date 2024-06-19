import datetime
import requests as r
import time
from database_populator import DatabaseManager
import pandas as pd

class ZipCodeUtility():
    def __init__(self, startyear=2012, endyear=None, api_headers=None):
        self.api_headers = api_headers
        self.base_url = "https://api.census.gov/data"
        self.startyear = startyear
        self.endyear = endyear
        if endyear is None:
            self.endyear = datetime.datetime.now().year - 1
        with DatabaseManager() as db_manager:
            self.db_manager = db_manager 
        self.failed_attempts = set()  # Initialize an empty set to track failed attempts


    # Gets data for one zipcode within a range of years
    def get_zip_zbp(self, industry):
        
        years = range(self.startyear, self.endyear+1)
        self.db_manager.open()

        for year in years:
            if (industry, year) in self.failed_attempts:  # Check if this combination has failed before
                print(f"Skipping industry data for industry: {industry} year: {year} due to previous failure")
                continue
            print(f"Getting industry data for industry: {industry}\tyear: {year}")
            data, status_code = self._get_response_data(industry, year)
            if status_code == 304:
                continue

            if status_code == 204 or status_code != 200:
                print(f"Failed to fetch data for year {year}: {status_code}")
                self.failed_attempts.add((industry, year)) 
                continue

            data_excluding_column_names = data[1:]
            batch_data = []

            for line in data_excluding_column_names:
                naics_code = str(line[1]).strip()

                row = self._create_row(naics_code, line, year)
                batch_data.append(row)

                if len(batch_data) >= 1000: 
                    self.db_manager.insert_data_entries(batch_data)
                    batch_data = []

            # Insert any remaining data that didn't meet the batch size requirement
            if batch_data:
                self.db_manager.insert_data_entries(batch_data)

            print(f"Finished processing {industry} for {year}.")
        self.db_manager.close()


   # Gets all zipcode data
    def get_all_zip_zbp(self):   
        industries = pd.read_csv('./id_lists/industry_id_list.csv')
        industries['relevant_naics'] = industries['relevant_naics'].astype(int).astype(str)
        industries['level'] = industries['relevant_naics'].apply(len)
        industries = industries[industries['level'].isin([2, 4, 6])]
        if not hasattr(industries, 'get') or 'relevant_naics' not in industries:
            raise ValueError("industries must be a dictionary-like object with a 'relevant_naics' key")

        for industry in industries['relevant_naics']:
            if industry == 0:
                self.get_zip_zbp('00')
            else:
                self.get_zip_zbp(industry)
    

    # Makes sure that commas don't mess up the csv. Also handles missing data.
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

    # Handles NAICS codes like '31-33' by returning the length of the first part
    def _valid_naics_level(self, naics_code):
        if '-' in naics_code:
            parts = naics_code.split('-')
            if all(part.isdigit() for part in parts):
                return len(parts[0])  
        return len(naics_code)


    # Creates the row that is to be appended
    def _create_row(self, naics_code, line, year):
        return [
            line[0],
            naics_code,
            year,
            line[2],  # Establishments
            line[3],  # Employees
            line[4],   # Payroll
            len(naics_code)

        ]
    
    def _get_response_data(self, sector, year, attempt=1):
        # Check if data already exists in the database
        if self.db_manager.data_for_year_and_sector_exists(year, sector):
            print(f"Data for sector {sector} and year {year} already exists in the database. Skipping API call.")
            return {}, 304  # 304 Not Modified
        code = self._naics_year_selector(year)
        if not isinstance(sector, str):
            sector = str(sector)
        if sector == '0':
            sector = '00'
        url = f"{self.base_url}/{year}/zbp?get=ZIPCODE,{code},ESTAB,EMP,PAYANN&for=zip%20code:*&{code}={sector}&key={self.api_headers['x-api-key']}"

        if year > 2018:
            url = f"{self.base_url}/{year}/cbp?get=ZIPCODE,{code},ESTAB,EMP,PAYANN&for=zip%20code:*&{code}={sector}&key={self.api_headers['x-api-key']}"
        response = r.get(url, headers=self.api_headers)

        # Added in the case that the api key isn't working
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
            print(f"Failed to fetch data: {response.status_code}")
            return {}, response.status_code
        
    def close_resources(self):
        """Close any resources such as database connections."""
        if self.db_manager:
            self.db_manager.close()

