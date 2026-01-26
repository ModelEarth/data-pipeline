### ZipCode Metrics List

# This code is generating a comprehensive list of all zipcodes that contain data for a given industry level.
# We are calculating the number of unique idustries, and total numbers for employees, establishments, and payroll
# The industry level is modifiable

# We achieve this using Pandas dataframes manipulation

import os
import json, requests, csv
import pandas as pd
import argparse
import sys
from datetime import datetime

def get_directory_size(path, exclude_dirs=None):
    """Calculate total size of all files in a directory, optionally excluding subdirectories"""
    total_size = 0
    if exclude_dirs is None:
        exclude_dirs = []

    if not os.path.exists(path):
        return 0

    for dirpath, dirnames, filenames in os.walk(path):
        # Remove excluded directories from the walk
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

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

def process_level(ind_level, year, output_path):
    """Process a single NAICS level"""
    url = f"https://api.census.gov/data/{year}/zbp?get=ZIPCODE,NAICS2017,ESTAB,EMPSZES,PAYANN&for=zipcode:*&INDLEVEL={ind_level}"

    print(f"\nProcessing NAICS level {ind_level}...")

    # Simple way to get all Data
    orig = pd.read_json(url)
    new_header = orig.iloc[0]
    orig = orig[1:]
    orig.columns = new_header

    # Converting to Integer Values
    int_df1 = orig.astype({'NAICS2017':'str', 'ESTAB' : 'int', 'EMPSZES' : 'int', 'PAYANN' : 'int', 'ZIPCODE' : 'str'})
    int_df = int_df1.rename({'ZIPCODE' : 'Zip', 'NAICS2017': 'Industries', 'ESTAB': 'Establishments', 'EMPSZES' : 'Employees', 'PAYANN' : 'Payroll'}, axis=1)

    # Grouping (Count Unique & Sum)
    gr1 = int_df[['Zip','Industries']].groupby(['Zip']).nunique()
    gr2 = int_df[['Zip','Establishments', 'Employees', 'Payroll']].groupby(['Zip']).sum()

    # Merging Grouped Dataframes
    combined = gr1.merge(gr2, left_on='Zip', right_on='Zip')
    final_df = combined

    # Exporting to CSV
    output_filename = f'{output_path}/zipcodes-naics{ind_level}-{year}.csv'
    final_df.to_csv(output_filename)
    print(f"  Exported: {os.path.basename(output_filename)} ({len(final_df):,} rows)")

    return {
        'level': ind_level,
        'filename': os.path.basename(output_filename),
        'rows': len(final_df),
        'file_size': os.path.getsize(output_filename)
    }

# Command-line argument parsing
parser = argparse.ArgumentParser(description='Generate aggregated zipcode metrics from Census ZBP data')
parser.add_argument('year', nargs='?', default='2018', help='Census data year (default: 2018)')
parser.add_argument('--naics-level', type=str, default='all', help='Industry level (2-6, or "all" for 2-6, default: all)')
parser.add_argument('--output-path', type=str, default='../../../community-data/US/zip', help='Output directory (default: ../../../community-data/US/zip)')
args = parser.parse_args()

year = args.year

# Determine which levels to process
if args.naics_level.lower() == 'all':
    levels_to_process = ['2', '3', '4', '5', '6']
    print(f"Processing all NAICS levels (2-6)")
else:
    levels_to_process = [args.naics_level]
    print(f"Processing NAICS level {args.naics_level}")

# Track start time
start_time = datetime.now()
start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

# Create output directory if it doesn't exist
if not os.path.exists(args.output_path):
    os.makedirs(args.output_path)
    print(f"Created output directory: {args.output_path}")

print(f"Sending to: {os.path.abspath(args.output_path)}")
print(f"Started: {start_time_str}")

# Process each level and collect results
all_results = []
for level in levels_to_process:
    result = process_level(level, year, args.output_path)
    all_results.append(result)

# Generate results.md after all levels complete
end_time = datetime.now()
end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
duration = end_time - start_time
duration_str = str(duration).split('.')[0]  # Remove microseconds

# Calculate directory size excluding 'naics' subfolder
total_size_bytes = get_directory_size(args.output_path, exclude_dirs=['naics'])
total_size_formatted = format_size(total_size_bytes)

script_location = os.path.abspath(__file__)
# Trim path to start from /data-pipeline
if '/data-pipeline' in script_location:
    script_location = '/data-pipeline' + script_location.split('/data-pipeline')[1]
results_file = f'{args.output_path}/results.md'

# Build file details section
files_section = ""
for result in all_results:
    file_size_formatted = format_size(result['file_size'])
    files_section += f"- **Level {result['level']}**: `{result['filename']}` - {result['rows']:,} rows, {file_size_formatted}\n"

# Determine command used
if args.naics_level.lower() == 'all':
    command_used = f"python zipcodes.py {year} --output-path {args.output_path}"
else:
    command_used = f"python zipcodes.py {year} --naics-level {args.naics_level} --output-path {args.output_path}"

results_content = f"""# Results - Zipcodes Aggregated Metrics

**Last successful completion:** {end_time_str}

## Execution Timeline

- **Start time:** {start_time_str}
- **End time:** {end_time_str}
- **Total run time:** {duration_str}

## Output Details

- **Number of files generated:** {len(all_results)}
- **NAICS levels processed:** {', '.join([r['level'] for r in all_results])}
- **Census year:** {year}
- **Total output size:** {total_size_formatted} (Excluding naics subfolder)

### Generated Files

{files_section}

## Generation Details

- **Generated by:** `{os.path.basename(script_location)}`
- **Script location:** `{script_location}`
- **Command:** `{command_used}`

## Data Summary

Each output file contains aggregated metrics for zipcodes with the following columns:
- Zip (zipcode)
- Industries (unique count at specified NAICS level)
- Establishments (total)
- Employees (total)
- Payroll (total)

**NAICS Levels:**
- Level 2: 2-digit codes (broad industry categories - 20 sectors)
- Level 3: 3-digit codes (subsectors)
- Level 4: 4-digit codes (industry groups)
- Level 5: 5-digit codes (NAICS industries)
- Level 6: 6-digit codes (national industries - most detailed)
"""

with open(results_file, 'w') as f:
    f.write(results_content)

print(f"\nResults saved to: {results_file}")
print(f"Completed: {end_time_str}")
print(f"Total run time: {duration_str}")
print(f"Total files generated: {len(all_results)}")
