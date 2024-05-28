import requests as r
import datetime
import requests as r
from pathlib import Path
import pickle
import time

class Pre2019ZipCodeUtility():
    def __init__(self, api_headers = None):
        self.year = datetime.date.today().year
        self.api_headers = api_headers
    
    # Finds and/or makes the zipcode directory for community data
    def zipcode_data_dir(self, zipcode, cache=False, year=None):
        base_path = Path('../../../community-data/industries/naics/US/zips')
        formatted_zip = str(zipcode).zfill(5)
        for num in formatted_zip:
            base_path /= num

        if year:
            base_path /= str(year)
        
        if cache:
            base_path /= 'cache'
        
        base_path.mkdir(parents=True, exist_ok=True)
        
        return base_path

    # Makes sure that commas don't mess up the csv. Also handles missing data.
    def escape_and_quote(self, item):
        if item is None or item == '':
            return '"0"'
        escaped_item = item.replace('"', '""')
        return f'"{escaped_item}"'

    # Handles NAICS codes like '31-33' by returning the length of the first part
    def valid_naics_level(self, naics_code):
        if '-' in naics_code:
            parts = naics_code.split('-')
            if all(part.isdigit() for part in parts):
                return len(parts[0])  
        return len(naics_code)

    # Selects proper NAICS code for specified year
    def naics_year_selector(self, year):
        if year >= 2000 and year <= 2002:
            return "NAICS1997"
        elif year >= 2003 and year <= 2007:
            return "NAICS2002"
        elif year >= 2008 and year <= 2011:
            return "NAICS2007"
        elif year >= 2012 and year <= 2016:
            return "NAICS2012"
        return "NAICS2017"

    # Makes file name and path
    def make_file_name(self, zipcode, year, naics_length):
        file_suffix = {2: 'naics2', 4: 'naics4', 6: 'naics6'}.get(naics_length, 'other')
        file_name = f"US-{zipcode:05d}-census-{year}-{file_suffix}.csv"
        return self.zipcode_data_dir(zipcode, year=None) / file_name


    # Creates edited headers if file does not already exist
    def make_edited_column_names(self, file_full_path, file_handlers):
        if file_full_path not in file_handlers:
            file_handlers[file_full_path] = open(file_full_path, 'w')
            headers = ["Zip", "NAICS", "Establishments", "Employees", "Payroll"]
            file_handlers[file_full_path].write(','.join(headers) + '\n')

    # Creates the row that is to be appended
    def create_row(self, zipcode, naics_code, line):
        return [
            str(zipcode).zfill(5),
            self.escape_and_quote(naics_code),
            self.escape_and_quote(line[1]),  # Establishments
            self.escape_and_quote(line[2]),  # Employees
            self.escape_and_quote(line[3])   # Payroll
        ]
    # Added caching just in case 
    def get_response_data(self, base_url, zipcode, year, api_headers, attempt=1):
        cache_dir = self.zipcode_data_dir(zipcode, cache=True, year=None)
        cache_file = cache_dir / f"{year}.pickle"

        if cache_file.exists():
            print(f"Loading cached data for ZIP code {zipcode}, year {year}")
            with open(cache_file, 'rb') as file:
                return pickle.load(file), 200

        url = f"{base_url}/{year}/zbp?get={self.naics_year_selector(year)},ESTAB,EMP,PAYANN&for=zipcode:{zipcode:05d}"
        response = r.get(url, headers=api_headers)

        # Added in the case that the api key isn't working
        if response.status_code == 429:  
            if attempt <= 5:  
                sleep_time = (2 ** attempt)
                print(f"Rate limit exceeded, retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                return self.get_response_data(base_url, zipcode, year, api_headers, attempt + 1)
            else:
                print("Max retry attempts reached, unable to retrieve data.")
                return {}, 429  

        if response.status_code == 200:
            data = response.json()
            with open(cache_file, 'wb') as file:
                pickle.dump(data, file)
            return data, 200
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            return {}, response.status_code


    # Gets data for one zipcode within a range of years
    def get_zip_zbp(self, zipcode, years, api_headers):
        base_url = "https://api.census.gov/data"
        file_handlers = {}
        for year in years:
            print(f"Getting data for zipcode: {zipcode}\tyear: {year}")
            data, status_code = self.get_response_data(base_url, zipcode, year, api_headers)
            
            if status_code != 200:
                print(f"Failed to fetch data for year {year}")
                continue
            
            data_exluding_column_names = data[1:]

            for line in data_exluding_column_names:
                naics_code = str(line[0]).strip()
                naics_level = self.valid_naics_level(naics_code)
                
                # Skips if NAICS code is not 2, 4, or 6 digits long
                if naics_level not in [2, 4, 6]:
                    continue  

                file_full_path = self.make_file_name(zipcode, year, naics_level)
                self.make_edited_column_names(file_full_path, file_handlers)
                row  = self.create_row(zipcode, naics_code, line)
                file_handlers[file_full_path].write(','.join(row) + '\n')

            print(f"Finished processing {zipcode} for {year}.")
        for handler in file_handlers.values():
            handler.close()

    # Gets all zipcode data
    def get_all_zip_zbp(self, zipcodes, startyear, endyear, api_headers):    
        for zipcode in zipcodes['Zip'].unique():
            years = range(startyear, endyear + 1)
            self.get_zip_zbp(zipcode, years, api_headers)