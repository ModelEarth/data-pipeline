# Zips
# Retrieving NAICS data for each (zip code, IND level) pair
# 2/23/2022

import os
import json, requests, csv
import pandas as pd
import argparse
from datetime import datetime

def get_directory_size(path):
    """Calculate total size of all files in a directory"""
    total_size = 0

    if not os.path.exists(path):
        return 0

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)

    return total_size

def format_size(bytes_size):
    """Format bytes into human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

# Command-line argument parsing
parser = argparse.ArgumentParser(description='Fetch Census ZBP data for zipcodes')
parser.add_argument('--zipcode', type=str, help='Single zipcode to process (e.g., 98006)')
parser.add_argument('--batch-start', type=int, help='Batch start index (0-99449)')
parser.add_argument('--batch-end', type=int, help='Batch end index (0-99449)')
parser.add_argument('--naics-level', type=str, default="2", help='Industry level (2-6, default: 2)')
parser.add_argument('--year', type=str, default="2018", help='Census data year (default: 2018)')
parser.add_argument('--output-path', type=str, default="../../../community-data/US/zip", help='Output directory path (default: ../../../community-data/US/zip)')
args = parser.parse_args()

inds = [args.naics_level]

# Track start time
start_time = datetime.now()
start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

# Create output directory if it doesn't exist
if not os.path.exists(args.output_path):
    os.makedirs(args.output_path)
    print(f"Created output directory: {args.output_path}")

print(f"Sending to: {os.path.abspath(args.output_path)}")
print(f"Started: {start_time_str}")

raw_nums = list(range(501,99951))
zips = []

for number in raw_nums: # appending 0's to begining of zip codes with <5 numbers
    if len(str(number)) == 3:
        zips.append("00" + str(number))
    elif len(str(number)) == 4:
        zips.append("0" + str(number))
    else:
        zips.append(str(number))

def create_folders(): # creates a folder for every zip code
    for each in zips:
        if not os.path.exists("zips/"+each): # check if directory for zipcode already there before
            os.makedirs("zips/"+each)

### Explanation of  zipcode() Function
### In the zipcode() function, we have a base url which retrieves all relevant data for a certain IND Level. We can loop through each IND
### level and therefore retrieve all data for whichever IND Levels we are interested in.

### Following, we create a response object containing the data and use .json() to get the data into a json format, which we then write
### to a file. Then we open the file, and create a pandas DF of all the data. To generate the zip code folders, we group the dataframe
### by the "Zip Code" column and export it as a .csv file into the corresponding folder within naics/zips/xxxxx

def create_zipcode_directory(zipcode, base_path):
    """Create nested directory structure for a zipcode"""
    path = base_path + "/" + zipcode[0]
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + "/" + zipcode[1]
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + "/" + zipcode[2]
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + "/" + zipcode[3]
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + "/" + zipcode[4]
    if not os.path.exists(path):
        os.makedirs(path)

def save_zipcode_data(df, zipcode, ind_level, year, base_path):
    """Save zipcode data to CSV in nested directory structure"""
    create_zipcode_directory(zipcode, base_path)
    filepath = base_path + "/" + zipcode[0] + "/" + zipcode[1] + "/" + zipcode[2] + "/" + zipcode[3] + "/" + zipcode[4] + "/zipcode-" + zipcode + "-census-naics" + ind_level + "-" + year + ".csv"
    zipcode_data = df.loc[df["Zip"] == zipcode].drop(columns=["Zip", "NaicsLevel"], axis = 1)
    zipcode_data.to_csv(filepath, index = False)
    print(f"Saved data for zipcode {zipcode}")
    return len(zipcode_data)  # Return row count

def zipcode(): # populates zip code folders with data for each zip
    total_zipcodes = 0
    total_rows = 0
    processed_zipcodes = []

    for j in inds:
        url = f"https://api.census.gov/data/{args.year}/zbp?get=ZIPCODE,NAICS2017,ESTAB,EMPSZES,PAYANN&for=zipcode:*&INDLEVEL={j}"
        response = requests.get(url)
        data = response.json()
        with open('ind_data.json', 'w') as f:
            json.dump(data, f)

        with open("ind_data.json", "r") as f2:
            jsdata = json.load(f2)

        df = pd.DataFrame(jsdata, columns = ["Zip", "Naics", "Establishments", "Employees", "Payroll", "NaicsLevel"])
        df['Employees'] =  df['Employees'].str.lstrip('0')

        # Determine which zipcodes to process
        if args.zipcode:
            # Single zipcode mode
            zipcode = args.zipcode.zfill(5)  # Ensure 5 digits
            if df.loc[df["Zip"] == zipcode].empty:
                print(f"No data found for zipcode {zipcode}")
            else:
                row_count = save_zipcode_data(df, zipcode, j, args.year, args.output_path)
                total_zipcodes += 1
                total_rows += row_count
                processed_zipcodes.append(zipcode)
        else:
            # Batch mode
            start = args.batch_start if args.batch_start is not None else 3000
            end = args.batch_end if args.batch_end is not None else 3500
            print(f"Processing batch: zips[{start}:{end}]")

            for num in zips[start:end]:
                if df.loc[df["Zip"] == num].empty:
                    continue
                row_count = save_zipcode_data(df, num, j, args.year, args.output_path)
                total_zipcodes += 1
                total_rows += row_count
                processed_zipcodes.append(num)

        print("Done with IND level " + j)

    # Generate results-naics.md
    end_time = datetime.now()
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    duration = end_time - start_time
    duration_str = str(duration).split('.')[0]  # Remove microseconds

    # Calculate total size of all files in output directory
    total_size_bytes = get_directory_size(args.output_path)
    total_size_formatted = format_size(total_size_bytes)

    script_location = os.path.abspath(__file__)
    # Trim path to start from /data-pipeline
    if '/data-pipeline' in script_location:
        script_location = '/data-pipeline' + script_location.split('/data-pipeline')[1]
    results_file = f'{args.output_path}/results-naics.md'

    # Determine mode description
    if args.zipcode:
        mode_desc = f"Single zipcode mode: {args.zipcode}"
        command_example = f"python zipcodes-naics.py --zipcode {args.zipcode} --naics-level {args.naics_level} --year {args.year}"
    else:
        start = args.batch_start if args.batch_start is not None else 3000
        end = args.batch_end if args.batch_end is not None else 3500
        mode_desc = f"Batch mode: indices {start}-{end}"
        command_example = f"python zipcodes-naics.py --batch-start {start} --batch-end {end} --naics-level {args.naics_level} --year {args.year}"

    results_content = f"""# Results - Zipcodes NAICS Detailed Data

**Last successful completion:** {end_time_str}

## Execution Timeline

- **Start time:** {start_time_str}
- **End time:** {end_time_str}
- **Total run time:** {duration_str}

## Output Details

- **Processing mode:** {mode_desc}
- **Number of zipcodes processed:** {total_zipcodes:,}
- **Total rows written:** {total_rows:,}
- **Industry level:** {args.naics_level}
- **Census year:** {args.year}
- **Output location:** `{args.output_path}/X/X/X/X/X/`
- **Total output size:** {total_size_formatted}

## Generation Details

- **Generated by:** `{os.path.basename(script_location)}`
- **Script location:** `{script_location}`
- **Command:** `{command_example} --output-path {args.output_path}`

## File Structure

Each zipcode creates a file at:
```
{args.output_path}/X/X/X/X/X/zipcode-<XXXXX>-census-naics{args.naics_level}-{args.year}.csv
```

## Data Summary

The output contains detailed NAICS industry data for each zipcode with the following columns:
- Naics (NAICS code)
- Establishments
- Employees
- Payroll

Total files created: {total_zipcodes:,}
"""

    with open(results_file, 'w') as f:
        f.write(results_content)

    print(f"Results saved to: {results_file}")
    print(f"Completed: {end_time_str}")
    print(f"Total run time: {duration_str}")

    return total_zipcodes, total_rows


def delete_empty(): # deletes zip folders without data in them
    dir = "zips"
    folders = list(os.walk(dir))[1:]

    for folder in folders:
        if not folder[2]:
            os.rmdir(folder[0])




### Function Calls
if __name__ == '__main__':
    if args.zipcode:
        print(f"Processing single zipcode: {args.zipcode}")
    elif args.batch_start is not None and args.batch_end is not None:
        print(f"Processing batch: indices {args.batch_start} to {args.batch_end}")
    else:
        print("Processing default batch: indices 3000 to 3500")

    zipcode()
    print("Complete...")

