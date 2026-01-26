### County Business Patterns (CBP) Data Pipeline
# Retrieves NAICS data at the county level from Census CBP API
# Generates CSV files for each state with county-level industry statistics

import os
import json
import requests
import pandas as pd
import argparse
from datetime import datetime
import yaml

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

def get_county_cbp(fips, state, year, api_key=None):
    """
    Fetch county-level CBP data from Census API for a specific state and year
    Returns a DataFrame with county-level NAICS data
    """
    base_url = "https://api.census.gov/data"
    headers = {}
    if api_key:
        headers['x-api-key'] = api_key

    # Select columns based on year (NAICS version changes by year)
    # 2022+ CBP API still uses NAICS2017 fields (latest available is 2023)
    if year >= 2017 and year <= 2024:
        columns_to_select = "GEO_ID,NAME,COUNTY,YEAR,NAICS2017,NAICS2017_LABEL,ESTAB,EMP,PAYANN"
    elif year >= 2012 and year <= 2016:
        columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2012,NAICS2012_TTL,ESTAB,EMP,PAYANN"
    elif year >= 2008 and year <= 2011:
        columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2007,NAICS2007_TTL,ESTAB,EMP,PAYANN"
    elif year >= 2003 and year <= 2007:
        columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2002,NAICS2002_TTL,ESTAB,EMP,PAYANN"
    elif year >= 2000 and year <= 2002:
        columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS1997,NAICS1997_TTL,ESTAB,EMP,PAYANN"
    else:
        raise ValueError(f"Year {year} not supported. Supported years: 2000-2024")

    url = f"{base_url}/{year}/cbp?get={columns_to_select}&for=county:*&in=state:{fips:02d}"

    response = None
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # First row is headers
        df = pd.DataFrame(data[1:], columns=data[0])

        return df
    except requests.exceptions.HTTPError as e:
        print(f"  Error fetching data for state FIPS {fips}, year {year}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching data for state FIPS {fips}, year {year}: {e}")
        return None

def process_county_data(df, year, drop_fips=False):
    """
    Process raw county CBP data into standardized format
    Handles different column names across different year ranges
    """
    if df is None or df.empty:
        return None

    # Determine column names based on year
    if year >= 2017:
        naics_col = "NAICS2017"
        name_col = "NAME"
    elif year >= 2012:
        naics_col = "NAICS2012"
        name_col = "GEO_TTL"
    elif year >= 2008:
        naics_col = "NAICS2007"
        name_col = "GEO_TTL"
    elif year >= 2003:
        naics_col = "NAICS2002"
        name_col = "GEO_TTL"
    else:
        naics_col = "NAICS1997"
        name_col = "GEO_TTL"

    # Rename to standard columns
    df = df.rename(columns={
        naics_col: "Naics",
        "ESTAB": "Establishments",
        "EMP": "Employees",
        "PAYANN": "Payroll"
    })

    # Extract FIPS from GEO_ID (format: 0500000US12345)
    df['Fips'] = df['GEO_ID'].apply(lambda gid: gid.split('US')[1] if 'US' in gid else gid)

    # Convert numeric columns
    df['Establishments'] = pd.to_numeric(df['Establishments'], errors='coerce').fillna(0).astype(int)
    df['Employees'] = pd.to_numeric(df['Employees'], errors='coerce').fillna(0).astype(int)
    df['Payroll'] = pd.to_numeric(df['Payroll'], errors='coerce').fillna(0).astype(int)

    # Filter out NAICS code "00" (totals)
    df = df[df['Naics'] != '00']

    # Select final columns
    if drop_fips:
        df = df[['Naics', 'Establishments', 'Employees', 'Payroll']]
    else:
        df = df[['Fips', 'Naics', 'Establishments', 'Employees', 'Payroll']]

    return df

def filter_by_naics_level(df, naics_level):
    """Filter dataframe to only include rows matching specified NAICS level"""
    return df[df['Naics'].str.len() == naics_level]

def check_year_available(year, api_key=None, dataset="cbp"):
    """Check Census API availability for the selected year before processing."""
    base_url = "https://api.census.gov/data"
    headers = {}
    if api_key:
        headers['x-api-key'] = api_key
    url = f"{base_url}/{year}/{dataset}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print(f"Year {year} is not available in the Census {dataset.upper()} API (HTTP 404).")
            return False
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError) and 'NameResolutionError' in str(e):
            print("Error checking CBP API: DNS resolution failed for api.census.gov. Check your network or DNS settings.")
            return False
        print(f"Error checking CBP API for year {year}: {e}")
        return False

# Command-line argument parsing
parser = argparse.ArgumentParser(description='Generate county-level NAICS data from Census CBP API')
parser.add_argument('year', nargs='?', default=None, help='Census data year (default: 2021)')
parser.add_argument('--naics-level', type=str, default=None, help='Industry level (2,4,6 or "all" for 2,4,6, default: all)')
parser.add_argument('--scope', type=str, help='Scope(s) to run: zip, county, state, country, or all. Comma-separated for multiple.')
parser.add_argument('--state', type=str, help='Two-letter state code to process single state (e.g., GA)')
parser.add_argument('--output-path', type=str, default=None, help='Output directory (default: ../../../community-data/industries/naics/US/counties-update)')
parser.add_argument('--api-key', type=str, help='Census API key (optional)')
args = parser.parse_args()

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}

config = load_config()

scopes = {
    'zip': 'zips',
    'county': 'counties',
    'state': 'states',
    'country': 'countries'
}

default_year = 2021
year = int(args.year or config.get('YEAR', default_year))
args.year = str(year)

args.naics_level = str(args.naics_level or config.get('NAICS_LEVEL', 'all'))
args.state = args.state or config.get('STATE')
args.output_path = args.output_path or config.get('OUTPUT_PATH', '../../../community-data/industries/naics/US/[scope]-update')
args.api_key = args.api_key or config.get('API_KEY')
state_fips_path = os.path.join(os.path.dirname(__file__), 'state-fips.csv')
output_path_template = args.output_path

def parse_scopes(raw_scope):
    if not raw_scope:
        return []
    scopes_list = [s.strip() for s in raw_scope.split(',') if s.strip()]
    if 'all' in scopes_list:
        return ['zip', 'county', 'state', 'country']
    return scopes_list

scope_selected_raw = args.scope or config.get('SCOPE', {}).get('selected', 'county')
scope_list = parse_scopes(scope_selected_raw)
if not scope_list:
    scope_list = ['county']

zip_dataset = "zbp" if year <= 2018 else "cbp"

def fetch_zip_data(year, ind_level, dataset, api_key=None):
    base_url = "https://api.census.gov/data"
    headers = {}
    if api_key:
        headers['x-api-key'] = api_key
    url = f"{base_url}/{year}/{dataset}?get=ZIPCODE,NAICS2017,ESTAB,EMPSZES,PAYANN&for=zipcode:*&INDLEVEL={ind_level}"
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        alt_url = f"{base_url}/{year}/{dataset}?get=ZIPCODE,NAICS2017,ESTAB,EMPSZES,PAYANN&for=zip%20code:*&INDLEVEL={ind_level}"
        response = requests.get(alt_url, headers=headers)
    response.raise_for_status()
    return response.json()

def process_zip_level(ind_level, year, output_path, dataset, api_key=None):
    print(f"\nProcessing NAICS level {ind_level}...")
    data = fetch_zip_data(year, ind_level, dataset, api_key)
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.astype({'NAICS2017': 'str', 'ESTAB': 'int', 'EMPSZES': 'int', 'PAYANN': 'int', 'ZIPCODE': 'str'})
    df = df.rename({'ZIPCODE': 'Zip', 'NAICS2017': 'Industries', 'ESTAB': 'Establishments', 'EMPSZES': 'Employees', 'PAYANN': 'Payroll'}, axis=1)
    gr1 = df[['Zip', 'Industries']].groupby(['Zip']).nunique()
    gr2 = df[['Zip', 'Establishments', 'Employees', 'Payroll']].groupby(['Zip']).sum()
    combined = gr1.merge(gr2, left_on='Zip', right_on='Zip')
    output_filename = f'{output_path}/zipcodes-naics{ind_level}-{year}.csv'
    combined.to_csv(output_filename)
    print(f"  Exported: {os.path.basename(output_filename)} ({len(combined):,} rows)")
    return {
        'level': ind_level,
        'filename': os.path.basename(output_filename),
        'rows': len(combined),
        'file_size': os.path.getsize(output_filename)
    }

def run_scope(scope_selected):
    scope_plural = scopes.get(scope_selected, scope_selected)
    scope_folder = "country" if scope_selected == "country" else scope_plural
    scope_suffix = "" if scope_selected in ["state", "country"] else f"-{scope_plural}"
    output_path = output_path_template.replace('[scope]', scope_folder)

    if args.naics_level.lower() == 'all':
        levels_to_process = [2, 4, 6]
        print(f"Processing NAICS levels 2, 4, 6")
    else:
        levels_to_process = [int(args.naics_level)]
        print(f"Processing NAICS level {args.naics_level}")

    start_time = datetime.now()
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created output directory: {output_path}")

    print(f"Sending to: {os.path.abspath(output_path)}")
    print(f"Started: {start_time_str}")

    check_dataset = zip_dataset if scope_selected == "zip" else "cbp"
    if not check_year_available(year, args.api_key, dataset=check_dataset):
        return

    if scope_selected == "zip":
        if args.naics_level.lower() == 'all':
            levels_to_process = [2, 3, 4, 5, 6]
        if year > 2018:
            print("ZIP scope for years 2019+ uses the CBP API (ZBP is only through 2018).")
        zip_results = []
        for level in [str(l) for l in levels_to_process]:
            result = process_zip_level(level, year, output_path, zip_dataset, args.api_key)
            zip_results.append(result)

        end_time = datetime.now()
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        duration = end_time - start_time
        duration_str = str(duration).split('.')[0]
        total_size_bytes = get_directory_size(output_path)
        total_size_formatted = format_size(total_size_bytes)

        script_location = os.path.abspath(__file__)
        if '/data-pipeline' in script_location:
            script_location = '/data-pipeline' + script_location.split('/data-pipeline')[1]
        results_file = f'{output_path}/results-zips.md'

        files_section = ""
        for result in zip_results:
            file_size_formatted = format_size(result['file_size'])
            files_section += f"- **Level {result['level']}**: `{result['filename']}` - {result['rows']:,} rows, {file_size_formatted}\n"

        scope_arg = f" --scope {scope_selected}"
        if args.naics_level.lower() == 'all':
            command_used = f"python annual.py {year}{scope_arg} --output-path {output_path}"
        else:
            command_used = f"python annual.py {year}{scope_arg} --naics-level {args.naics_level} --output-path {output_path}"

        results_content = f"""# Results - Zipcodes Aggregated Metrics

**Last successful completion:** {end_time_str}

## Execution Timeline

- **Start time:** {start_time_str}
- **End time:** {end_time_str}
- **Total run time:** {duration_str}

## Output Details

- **Number of files generated:** {len(zip_results)}
- **NAICS levels processed:** {', '.join([r['level'] for r in zip_results])}
- **Census year:** {year}
- **Total output size:** {total_size_formatted}

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
"""

        with open(results_file, 'w') as f:
            f.write(results_content)

        print(f"\nResults saved to: {results_file}")
        print(f"Completed: {end_time_str}")
        print(f"Total run time: {duration_str}")
        print(f"Total files generated: {len(zip_results)}")
        return

    # Load state FIPS codes
    try:
        state_fips = pd.read_csv(state_fips_path, usecols=['StateName', 'State', 'FIPS'])
        state_fips = state_fips.head(50)  # Limit to 50 US states, not territories
    except FileNotFoundError:
        print(f"Error: Could not find state FIPS file at {state_fips_path}")
        return

    # Filter to single state if specified
    if args.state:
        state_fips = state_fips[state_fips['State'] == args.state.upper()]
        if state_fips.empty:
            print(f"Error: State code '{args.state}' not found")
            return
        print(f"Processing single state: {args.state.upper()}")
    else:
        print(f"Processing all 50 states")

    # Track results for summary
    all_results = []
    total_files = 0
    country_level_frames = {lvl: [] for lvl in levels_to_process} if scope_selected == "country" else None

    for idx, row in state_fips.iterrows():
        fips = row['FIPS']
        state_name = row['StateName']
        state_code = row['State']

        print(f"\nProcessing {state_code} ({state_name})...")

        state_dir = os.path.join(output_path, state_code)
        if scope_selected != "country":
            if not os.path.exists(state_dir):
                os.makedirs(state_dir)

        raw_df = get_county_cbp(fips, state_name, year, args.api_key)

        if raw_df is None or raw_df.empty:
            print(f"  No data available for {state_code}")
            continue

        processed_df = process_county_data(raw_df, year, drop_fips=(scope_selected in ["state", "country"]))

        if processed_df is None or processed_df.empty:
            print(f"  No data after processing for {state_code}")
            continue

        state_results = {'state': state_code, 'files': []}

        if scope_selected == "country":
            for level in levels_to_process:
                level_df = filter_by_naics_level(processed_df, level)
                if level_df.empty:
                    continue
                country_level_frames[level].append(level_df)
            continue

        for level in levels_to_process:
            level_df = filter_by_naics_level(processed_df, level)

            if level_df.empty:
                print(f"  No data for level {level}")
                continue

            filename = f"US-{state_code}-census-naics{level}{scope_suffix}-{year}.csv"
            filepath = os.path.join(state_dir, filename)
            level_df.to_csv(filepath, index=False)

            file_size = os.path.getsize(filepath)
            row_count = len(level_df)

            print(f"  Saved: {filename} ({row_count:,} rows, {format_size(file_size)})")

            state_results['files'].append({
                'level': level,
                'filename': filename,
                'rows': row_count,
                'file_size': file_size
            })
            total_files += 1

        if state_results['files']:
            all_results.append(state_results)

    if scope_selected == "country":
        country_results = {'state': 'US', 'files': []}
        for level in levels_to_process:
            frames = country_level_frames.get(level, [])
            if not frames:
                continue
            combined = pd.concat(frames, ignore_index=True)
            combined = combined.groupby('Naics', as_index=False)[['Establishments', 'Employees', 'Payroll']].sum()
            filename = f"US-census-naics{level}-{year}.csv"
            filepath = os.path.join(output_path, filename)
            combined.to_csv(filepath, index=False)
            file_size = os.path.getsize(filepath)
            row_count = len(combined)
            print(f"  Saved: {filename} ({row_count:,} rows, {format_size(file_size)})")
            country_results['files'].append({
                'level': level,
                'filename': filename,
                'rows': row_count,
                'file_size': file_size
            })
            total_files += 1
        if country_results['files']:
            all_results = [country_results]

    end_time = datetime.now()
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    duration = end_time - start_time
    duration_str = str(duration).split('.')[0]

    total_size_bytes = get_directory_size(output_path)
    total_size_formatted = format_size(total_size_bytes)

    script_location = os.path.abspath(__file__)
    if '/data-pipeline' in script_location:
        script_location = '/data-pipeline' + script_location.split('/data-pipeline')[1]
    results_file = f'{output_path}/results-{scope_folder}.md'

    files_section = ""
    for state_result in all_results:
        state = state_result['state']
        files_section += f"\n### {state}\n"
        for file_info in state_result['files']:
            file_size_formatted = format_size(file_info['file_size'])
            files_section += f"- **Level {file_info['level']}**: `{file_info['filename']}` - {file_info['rows']:,} rows, {file_size_formatted}\n"

    scope_arg = f" --scope {scope_selected}"
    state_filter = f" --state {args.state}" if args.state else ""
    if args.naics_level.lower() == 'all':
        command_used = f"python annual.py {year}{scope_arg}{state_filter} --output-path {output_path}"
    else:
        command_used = f"python annual.py {year}{scope_arg} --naics-level {args.naics_level}{state_filter} --output-path {output_path}"

    processing_scope = f"Single state: {args.state.upper()}" if args.state else f"All 50 states"
    states_processed = len(all_results)
    columns_block = "- Naics (NAICS code at specified level)\n- Establishments (number of establishments)\n- Employees (total employees)\n- Payroll (total annual payroll in $1000s)"
    if scope_selected not in ["state", "country"]:
        columns_block = "- Fips (5-digit county FIPS code)\n" + columns_block

    results_title = "Results - Country CBP Data" if scope_selected == "country" else f"Results - {scope_plural.title()} CBP Data"
    filename_convention = f"US-census-naics<level>-<year>.csv" if scope_selected == "country" else f"US-<STATE>-census-naics<level>{scope_suffix}-<year>.csv"

    results_content = f"""# {results_title}

**Last successful completion:** {end_time_str}

## Execution Timeline

- **Start time:** {start_time_str}
- **End time:** {end_time_str}
- **Total run time:** {duration_str}

## Output Details

- **Processing scope:** {processing_scope}
- **States processed:** {states_processed}
- **Total files generated:** {total_files}
- **NAICS levels processed:** {', '.join([str(l) for l in levels_to_process])}
- **Census year:** {year}
- **Total output size:** {total_size_formatted}

### Generated Files
{files_section}

## Generation Details

- **Generated by:** `{os.path.basename(script_location)}`
- **Script location:** `{script_location}`
- **Command:** `{command_used}`

## Data Summary

Each output file contains CBP data with the following columns:
{columns_block}

**File Naming Convention:**
```
{filename_convention}
```

**NAICS Levels:**
- Level 2: 2-digit codes (broad industry categories - 20 sectors)
- Level 4: 4-digit codes (industry groups)
- Level 6: 6-digit codes (national industries - most detailed)

**Data Source:** Census Bureau County Business Patterns (CBP) API
"""

    with open(results_file, 'w') as f:
        f.write(results_content)

    print(f"\nResults saved to: {results_file}")
    print(f"Completed: {end_time_str}")
    print(f"Total run time: {duration_str}")
    print(f"Total files generated: {total_files}")

for scope_selected in scope_list:
    run_scope(scope_selected)
