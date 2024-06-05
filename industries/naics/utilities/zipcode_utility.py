import requests as r
import datetime
import requests as r
from pathlib import Path
import pickle
import time
import os

default_path = '../../../community-data/industries/naics/US/zips'

class ZipCodeUtility():
    def __init__(self, startyear = 2000, endyear = None, api_headers = None, base_path = default_path):
        self.api_headers = api_headers
        self.base_url = "https://api.census.gov/data"
        if endyear is None:
            endyear = datetime.datetime.now().year - 1
        if self._validate_inputs(base_path, startyear, endyear):
            self.years = range(startyear, endyear + 1)
            self.base_path = Path(base_path)
    
    # Gets data for one zipcode within a range of years
    def get_zip_zbp(self, zipcode):
        cache_dir = self._zipcode_data_dir(zipcode, cache=True, year=None)
        file_handlers = {}
        for year in self.years:
            print(f"Getting data for zipcode: {zipcode}\tyear: {year}")
            data, status_code = self._get_response_data(zipcode, year, cache_dir)
            
            if status_code != 200:
                print(f"Failed to fetch data for year {year}")
                continue
            
            data_exluding_column_names = data[1:]

            for line in data_exluding_column_names:
                naics_code = str(line[0]).strip()
                naics_level = self._valid_naics_level(naics_code)
                
                # Skips if NAICS code is not 2, 4, or 6 digits long
                if naics_level not in [2, 4, 6]:
                    continue  

                file_full_path = self._make_file_name(zipcode, year, naics_level)
                self._make_edited_column_names(file_full_path, file_handlers)
                row  = self._create_row(zipcode, naics_code, line)
                file_handlers[file_full_path].write(','.join(row) + '\n')

            print(f"Finished processing {zipcode} for {year}.")
        for handler in file_handlers.values():
            handler.close()

    # Gets all zipcode data
    def get_all_zip_zbp(self, zipcodes):   
        if not hasattr(zipcodes, 'get') or 'Zip' not in zipcodes:
            raise ValueError("zipcodes must be a dictionary-like object with a 'Zip' key")

        for zipcode in zipcodes['Zip'].unique():
            self.get_zip_zbp(zipcode)
    
    # Finds and/or makes the zipcode directory for community data
    def _zipcode_data_dir(self, zipcode, cache=False, year=None):
        zip_path = self.base_path
        formatted_zip = str(zipcode).zfill(5)
        for num in formatted_zip:
            zip_path /= num

        if year:
            zip_path /= str(year)
        
        if cache:
            zip_path /= 'cache'
        
        zip_path.mkdir(parents=True, exist_ok=True)
        
        return zip_path

    # Makes sure that commas don't mess up the csv. Also handles missing data.
    def _escape_and_quote(self, item):
        if item is None or item == '':
            return '"0"'
        escaped_item = item.replace('"', '""')
        return f'"{escaped_item}"'
    
    def _validate_inputs(self, base_path, startYear, endYear):
        # Check if the directory is valid
        if not os.path.exists(base_path):
            raise ValueError(f"Path does not exist: {base_path}")
        if not os.path.isdir(base_path):
            raise ValueError(f"Path is not a directory: {base_path}")
        if not os.access(base_path, os.W_OK):
            raise ValueError(f"No write permission on the directory: {base_path}")

        # Check if the year inputs are valid
        current_year = datetime.datetime.now().year
        if endYear > current_year:
            raise ValueError(f"Invalid end year: {endYear} - Cannot be greater than the current year {current_year}")
        if startYear < 2000:
            raise ValueError(f"Invalid start year: {startYear} - Must be 2000 or later")

        return True  # If all checks pass

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

    # Makes file name and path
    def _make_file_name(self, zipcode, year, naics_length):
        file_suffix = {2: 'naics2', 4: 'naics4', 6: 'naics6'}.get(naics_length, 'other')
        file_name = f"US-{zipcode:05d}-census-{year}-{file_suffix}.csv"
        return self._zipcode_data_dir(zipcode, year=None) / file_name


    # Creates edited headers if file does not already exist
    def _make_edited_column_names(self, file_full_path, file_handlers):
        if file_full_path not in file_handlers:
            file_handlers[file_full_path] = open(file_full_path, 'w')
            headers = ["Zip", "NAICS", "Establishments", "Employees", "Payroll"]
            file_handlers[file_full_path].write(','.join(headers) + '\n')

    # Creates the row that is to be appended
    def _create_row(self, zipcode, naics_code, line):
        return [
            str(zipcode).zfill(5),
            self._escape_and_quote(naics_code),
            self._escape_and_quote(line[1]),  # Establishments
            self._escape_and_quote(line[2]),  # Employees
            self._escape_and_quote(line[3])   # Payroll
        ]
    
    # Added caching just in case 
    def _get_response_data(self, zipcode, year, cache_dir, attempt=1):
        cache_file = cache_dir / f"{year}.pickle"

        if cache_file.exists():
            print(f"Loading cached data for {zipcode}, year {year}")
            with open(cache_file, 'rb') as file:
                return pickle.load(file), 200

        url = f"{self.base_url}/{year}/zbp?get={self._naics_year_selector(year)},ESTAB,EMP,PAYANN&for=zipcode:{zipcode:05d}"

        if year > 2018:
            url = f"{self.base_url}/{year}/cbp?get={self._naics_year_selector(year)},ESTAB,EMP,PAYANN&for=zipcode:{zipcode:05d}"
   
        response = r.get(url, headers=self.api_headers)

        # Added in the case that the api key isn't working
        if response.status_code == 429:  
            if attempt <= 5:  
                sleep_time = (2 ** attempt)
                print(f"Rate limit exceeded, retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                return self._get_response_data(zipcode, year, attempt + 1)
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
        

    # Property getters and setters
    @property
    def api_headers(self):
        return self._api_headers

    @api_headers.setter
    def api_headers(self, value):
        self._api_headers = value

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, value):
        self._base_path = Path(value)

    @property
    def years(self):
        return self._years

    @years.setter
    def years(self, start, end):
        self._years = range(start, end + 1)