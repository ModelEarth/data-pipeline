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
import sys

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
parser.add_argument('year', nargs='?', default=None, help='Census data year or comma-separated years (default: 2021)')
parser.add_argument('--naics-level', type=str, default=None, help='Industry level (2,4,6 or "all" for 2,4,6, default: all)')
parser.add_argument('--scope', type=str, help='Scope(s) to run: zip, ziptotal, county, state, country, or all. Comma-separated for multiple.')
parser.add_argument('--zip-batch-size', type=int, default=50, help='Pre-2017 ZIP batching: max NAICS codes to fetch per run (default: 50)')
parser.add_argument('--zip-max-minutes', type=int, default=120, help='Max minutes to keep running pre-2017 ZIP batching (default: 120)')
parser.add_argument('--zip-batch-minutes', type=int, default=20, help='Soft cap per batch window in minutes before writing a progress report (default: 20)')
parser.add_argument('--retry-failed', action='store_true', help='Pre-2017 ZIP batching: retry failed NAICS codes from the failed log (connection-related errors only)')
parser.add_argument('--zip-export-only', action='store_true', help='Pre-2017 ZIP batching: export from existing DuckDB files without refetching')
parser.add_argument('--delete-duckdb', action='store_true', help='Delete pre-2017 ZIP DuckDB files after a successful export')
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
    'ziptotal': 'zipstotal',
    'county': 'counties',
    'state': 'states',
    'country': 'countries'
}

def parse_years(raw_year):
    if not raw_year:
        return []
    if str(raw_year).strip().lower() == 'all':
        current_year = datetime.now().year
        return [str(y) for y in range(2000, current_year)]
    years = [y.strip() for y in str(raw_year).split(',') if y.strip()]
    return years

default_year = 2021
raw_year = args.year or config.get('YEAR', default_year)
year_list = parse_years(raw_year)
if not year_list:
    year_list = [str(default_year)]
census_years_str = ", ".join(year_list)

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
        return ['zip', 'ziptotal', 'county', 'state', 'country']
    return scopes_list

scope_selected_raw = args.scope or config.get('SCOPE', {}).get('selected', 'county')
scope_list = parse_scopes(scope_selected_raw)
if not scope_list:
    scope_list = ['county']

def fetch_zip_data(year, dataset, api_key=None, use_indlevel=True, ind_level=None, naics_filter=None):
    base_url = "https://api.census.gov/data"
    headers = {}
    if api_key:
        headers['x-api-key'] = api_key
    naics_field = "NAICS2017" if year >= 2017 else "NAICS2012"
    if use_indlevel:
        url = f"{base_url}/{year}/{dataset}?get=ZIPCODE,{naics_field},ESTAB,EMPSZES,PAYANN&for=zipcode:*&INDLEVEL={ind_level}"
    elif naics_filter:
        url = f"{base_url}/{year}/{dataset}?get=ZIPCODE,{naics_field},ESTAB,EMPSZES,PAYANN&for=zipcode:*&{naics_field}={naics_filter}"
    else:
        url = f"{base_url}/{year}/{dataset}?get=ZIPCODE,{naics_field},ESTAB,EMPSZES,PAYANN&for=zipcode:*"
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        if use_indlevel:
            alt_url = f"{base_url}/{year}/{dataset}?get=ZIPCODE,{naics_field},ESTAB,EMPSZES,PAYANN&for=zip%20code:*&INDLEVEL={ind_level}"
        elif naics_filter:
            alt_url = f"{base_url}/{year}/{dataset}?get=ZIPCODE,{naics_field},ESTAB,EMPSZES,PAYANN&for=zip%20code:*&{naics_field}={naics_filter}"
        else:
            alt_url = f"{base_url}/{year}/{dataset}?get=ZIPCODE,{naics_field},ESTAB,EMPSZES,PAYANN&for=zip%20code:*"
        response = requests.get(alt_url, headers=headers)
    response.raise_for_status()
    try:
        return response.json(), naics_field
    except requests.exceptions.JSONDecodeError:
        preview = response.text[:200].replace('\n', ' ')
        raise ValueError(f"Non-JSON response from Census API: {preview}")

def build_zip_df(data, naics_field):
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.loc[:, ~pd.Index(df.columns).duplicated()]
    df = df.astype({naics_field: 'str', 'ESTAB': 'int', 'EMPSZES': 'int', 'PAYANN': 'int', 'ZIPCODE': 'str'})
    df = df.rename({'ZIPCODE': 'Zip', naics_field: 'Naics', 'ESTAB': 'Establishments', 'EMPSZES': 'Employees', 'PAYANN': 'Payroll'}, axis=1)
    return df[['Zip', 'Naics', 'Establishments', 'Employees', 'Payroll']]

def is_retryable_error(error):
    if isinstance(error, requests.exceptions.RequestException):
        return True
    message = str(error).lower()
    retry_hints = [
        'timed out',
        'timeout',
        'temporary failure',
        'name or service not known',
        'dns',
        'connection reset',
        'connection aborted',
        'connection refused',
        'remote disconnected',
        'remote end closed connection',
        '502',
        '503',
        '504'
    ]
    return any(hint in message for hint in retry_hints)

def read_failed_codes(path):
    if not os.path.exists(path):
        return {}
    try:
        df = pd.read_csv(path, dtype=str)
        if df.empty:
            return {}
        return {row['code']: row for _, row in df.iterrows()}
    except Exception:
        return {}

def write_failed_codes(path, failed_by_code):
    if not failed_by_code:
        if os.path.exists(path):
            os.remove(path)
        return
    df = pd.DataFrame(list(failed_by_code.values()))
    df.to_csv(path, index=False)

_ZIP_STATE_MAP = None
def get_zip_state_mapping_path():
    return os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        'zip-state-geonames.tsv'
    ))

def load_zip_state_map():
    global _ZIP_STATE_MAP
    if _ZIP_STATE_MAP is not None:
        return _ZIP_STATE_MAP
    mapping_path = get_zip_state_mapping_path()
    if not os.path.exists(mapping_path):
        print(f"Warning: ZIP-to-state mapping not found at {mapping_path}. ZIP outputs will not be split by state.")
        _ZIP_STATE_MAP = None
        return None
    # State subfolders are used to split up files that exceed 17MB.
    # Source: GeoNames postal code dataset (US.zip) from download.geonames.org/export/zip/
    cols = ['country', 'zip', 'place', 'state_name', 'state', 'county_name', 'county', 'community_name', 'community', 'lat', 'lng', 'accuracy']
    df = pd.read_csv(mapping_path, sep='\t', header=None, names=cols, dtype={'zip': str, 'state': str, 'country': str})
    df = df[df['country'] == 'US']
    df['zip'] = df['zip'].str.zfill(5)
    df = df.drop_duplicates(subset=['zip'])
    _ZIP_STATE_MAP = df[['zip', 'state']].rename(columns={'zip': 'GeoID', 'state': 'State'})
    return _ZIP_STATE_MAP

def load_industry_codes(level_len):
    # Note: industry_id_list.csv is a legacy list; there may be better, newer sources.
    # DuckDB can be more efficient than pandas for large multi-year ZIP workloads due to lower memory usage and faster aggregations.
    industry_path = os.path.join(os.path.dirname(__file__), 'industry_id_list.csv')
    if not os.path.exists(industry_path):
        print(f"Error: Missing industry list at {industry_path}")
        return []
    df = pd.read_csv(industry_path)
    codes = df['relevant_naics'].dropna().astype(str).str.replace(r'\.0$', '', regex=True)
    codes = codes[codes.str.fullmatch(r'\d+')]
    codes = codes[codes.str.len() == level_len]
    codes = codes[codes != '00']
    codes = codes.unique().tolist()
    return codes

def get_duckdb_conn(db_path):
    try:
        import duckdb
    except ImportError as e:
        raise ImportError("duckdb is required for pre-2017 ZIP batching. Install with: pip install duckdb") from e
    return duckdb.connect(db_path)

def ensure_zip_state_temp(conn, mapping_path):
    conn.execute("""
        CREATE OR REPLACE TEMP TABLE zip_state AS
        SELECT
            lpad(zip, 5, '0') AS Zip,
            state AS State
        FROM read_csv(
            ?,
            delim='\\t',
            header=false,
            columns={
                'country':'VARCHAR',
                'zip':'VARCHAR',
                'place':'VARCHAR',
                'state_name':'VARCHAR',
                'state':'VARCHAR',
                'county_name':'VARCHAR',
                'county':'VARCHAR',
                'community_name':'VARCHAR',
                'community':'VARCHAR',
                'lat':'DOUBLE',
                'lng':'DOUBLE',
                'accuracy':'VARCHAR'
            }
        )
        WHERE country = 'US'
    """, [mapping_path])

def ensure_duckdb_zip_tables(conn, mapping_path):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS zip_rows (
            Zip TEXT,
            Naics TEXT,
            Establishments INTEGER,
            Employees INTEGER,
            Payroll INTEGER
        )
    """)
    conn.execute("CREATE TABLE IF NOT EXISTS loaded_codes (code TEXT PRIMARY KEY)")
    ensure_zip_state_temp(conn, mapping_path)

def export_zip_detail_duckdb(conn, output_path, level, year, mapping_path=None):
    mapping_path = mapping_path or get_zip_state_mapping_path()
    ensure_zip_state_temp(conn, mapping_path)
    mapping_path_sql = mapping_path.replace("'", "''")
    states = [row[0] for row in conn.execute("SELECT DISTINCT State FROM zip_state WHERE State IS NOT NULL AND State <> '' ORDER BY State").fetchall()]
    total_size = 0
    total_rows = 0
    for state in states:
        state_dir = os.path.join(output_path, state)
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
        output_filename = f'{state_dir}/US-{state}-zipcodes-naics{level}-{year}.csv'
        output_sql = output_filename.replace("'", "''")
        conn.execute(f"""
            COPY (
                SELECT zr.Zip, zr.Naics, zr.Establishments, zr.Employees, zr.Payroll
                FROM zip_rows zr
                JOIN (
                    SELECT lpad(zip, 5, '0') AS Zip, state AS State
                    FROM read_csv(
                        '{mapping_path_sql}',
                        delim='\\t',
                        header=false,
                        columns={{
                            'country':'VARCHAR',
                            'zip':'VARCHAR',
                            'place':'VARCHAR',
                            'state_name':'VARCHAR',
                            'state':'VARCHAR',
                            'county_name':'VARCHAR',
                            'county':'VARCHAR',
                            'community_name':'VARCHAR',
                            'community':'VARCHAR',
                            'lat':'DOUBLE',
                            'lng':'DOUBLE',
                            'accuracy':'VARCHAR'
                        }}
                    )
                    WHERE country = 'US'
                ) zs ON zr.Zip = zs.Zip
                WHERE zs.State = ?
            ) TO '{output_sql}' (HEADER, DELIMITER ',')
        """, [state])
        if os.path.exists(output_filename):
            total_size += os.path.getsize(output_filename)
            total_rows += conn.execute("""
                SELECT COUNT(*) FROM zip_rows zr
                JOIN zip_state zs ON zr.Zip = zs.Zip
                WHERE zs.State = ?
            """, [state]).fetchone()[0]

    # Not specified bucket for ZIPs without a state mapping
    not_dir = os.path.join(output_path, "NotSpecified")
    if not os.path.exists(not_dir):
        os.makedirs(not_dir)
    not_filename = f'{not_dir}/US-NotSpecified-zipcodes-naics{level}-{year}.csv'
    not_sql = not_filename.replace("'", "''")
    conn.execute(f"""
        COPY (
            SELECT zr.Zip, zr.Naics, zr.Establishments, zr.Employees, zr.Payroll
            FROM zip_rows zr
            LEFT JOIN (
                SELECT lpad(zip, 5, '0') AS Zip, state AS State
                FROM read_csv(
                    '{mapping_path_sql}',
                    delim='\\t',
                    header=false,
                    columns={{
                        'country':'VARCHAR',
                        'zip':'VARCHAR',
                        'place':'VARCHAR',
                        'state_name':'VARCHAR',
                        'state':'VARCHAR',
                        'county_name':'VARCHAR',
                        'county':'VARCHAR',
                        'community_name':'VARCHAR',
                        'community':'VARCHAR',
                        'lat':'DOUBLE',
                        'lng':'DOUBLE',
                        'accuracy':'VARCHAR'
                    }}
                )
                WHERE country = 'US'
            ) zs ON zr.Zip = zs.Zip
            WHERE zs.State IS NULL OR zs.State = ''
        ) TO '{not_sql}' (HEADER, DELIMITER ',')
    """)
    if os.path.exists(not_filename):
        total_size += os.path.getsize(not_filename)
        total_rows += conn.execute("""
            SELECT COUNT(*) FROM zip_rows zr
            LEFT JOIN zip_state zs ON zr.Zip = zs.Zip
            WHERE zs.State IS NULL OR zs.State = ''
        """).fetchone()[0]

    print(f"  Exported: US-<STATE>-zipcodes-naics{level}-{year}.csv ({total_rows:,} rows)")
    return {
        'level': level,
        'filename': f'US-<STATE>-zipcodes-naics{level}-{year}.csv',
        'rows': total_rows,
        'file_size': total_size
    }

def export_zip_total_duckdb(conn, output_path, level, year):
    output_filename = f'{output_path}/zipcodes-naics{level}-{year}.csv'
    output_sql = output_filename.replace("'", "''")
    conn.execute(f"""
        COPY (
            SELECT
                Zip,
                COUNT(DISTINCT Naics) AS Industries,
                SUM(Establishments) AS Establishments,
                SUM(Employees) AS Employees,
                SUM(Payroll) AS Payroll
            FROM zip_rows
            GROUP BY Zip
        ) TO '{output_sql}' (HEADER, DELIMITER ',')
    """)
    print(f"  Exported: {os.path.basename(output_filename)}")
    return {
        'level': level,
        'filename': os.path.basename(output_filename),
        'rows': conn.execute("SELECT COUNT(*) FROM zip_rows").fetchone()[0],
        'file_size': os.path.getsize(output_filename)
    }

def write_zip_total(df, ind_level, year, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    gr1 = df[['Zip', 'Naics']].groupby(['Zip']).nunique()
    gr2 = df[['Zip', 'Establishments', 'Employees', 'Payroll']].groupby(['Zip']).sum()
    combined = gr1.merge(gr2, left_on='Zip', right_on='Zip')
    combined = combined.rename(columns={'Naics': 'Industries'})
    output_filename = f'{output_path}/zipcodes-naics{ind_level}-{year}.csv'
    combined.to_csv(output_filename)
    print(f"  Exported: {os.path.basename(output_filename)} ({len(combined):,} rows)")
    return {
        'level': ind_level,
        'filename': os.path.basename(output_filename),
        'rows': len(combined),
        'file_size': os.path.getsize(output_filename)
    }

def write_zip_detail(df, ind_level, year, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    state_map = load_zip_state_map()
    if state_map is None:
        output_filename = f'{output_path}/zipcodes-naics{ind_level}-{year}.csv'
        df.to_csv(output_filename, index=False)
        print(f"  Exported: {os.path.basename(output_filename)} ({len(df):,} rows)")
        return {
            'level': ind_level,
            'filename': os.path.basename(output_filename),
            'rows': len(df),
            'file_size': os.path.getsize(output_filename)
        }

    merged = df.merge(state_map, left_on='Zip', right_on='GeoID', how='left')
    merged = merged.drop(columns=['GeoID'])
    merged['State'] = merged['State'].fillna('NotSpecified')

    total_size = 0
    for state, state_df in merged.groupby('State'):
        state_dir = os.path.join(output_path, state)
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
        output_filename = f'{state_dir}/US-{state}-zipcodes-naics{ind_level}-{year}.csv'
        state_df[['Zip', 'Naics', 'Establishments', 'Employees', 'Payroll']].to_csv(output_filename, index=False)
        total_size += os.path.getsize(output_filename)
    print(f"  Exported: US-<STATE>-zipcodes-naics{ind_level}-{year}.csv ({len(merged):,} rows)")
    return {
        'level': ind_level,
        'filename': f'US-<STATE>-zipcodes-naics{ind_level}-{year}.csv',
        'rows': len(merged),
        'file_size': total_size
    }

def run_scope(year, scope_selected, effective_years):
    scope_plural = scopes.get(scope_selected, scope_selected)
    scope_folder = "country" if scope_selected == "country" else scope_plural
    scope_suffix = "" if scope_selected in ["state", "country"] else f"-{scope_plural}"
    output_path = output_path_template.replace('[scope]', scope_folder)
    zip_dataset = "zbp" if year <= 2018 else "cbp"

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

    check_dataset = zip_dataset if scope_selected in ["zip", "ziptotal"] else "cbp"
    if not (args.zip_export_only and scope_selected in ["zip", "ziptotal"] and year < 2017):
        if not check_year_available(year, args.api_key, dataset=check_dataset):
            return

    if scope_selected in ["zip", "ziptotal"]:
        if args.naics_level.lower() == 'all':
            levels_to_process = [2, 3, 4, 5, 6]
        if year > 2018:
            print("ZIP scope for years 2019+ uses the CBP API (ZBP is only through 2018).")
        zip_results = []
        duckdb_files_to_delete = []
        zip_use_indlevel = not (zip_dataset == "zbp" and year < 2017)
        for level in [str(l) for l in levels_to_process]:
            print(f"\nProcessing NAICS level {level}...")
            if zip_use_indlevel:
                data, naics_field = fetch_zip_data(year, zip_dataset, args.api_key, use_indlevel=True, ind_level=level)
                level_df = build_zip_df(data, naics_field)
            else:
                db_path = os.path.join(output_path, f'zip-pre2017-{year}-naics{level}.duckdb')
                failed_log_path = os.path.join(output_path, f'zip-pre2017-failed-{year}-naics{level}.csv')
                failed_by_code = read_failed_codes(failed_log_path)
                if args.zip_export_only:
                    if not os.path.exists(db_path):
                        print(f"  Missing DuckDB file at {db_path}. Skipping export.")
                        continue
                    conn = get_duckdb_conn(db_path)
                    ensure_duckdb_zip_tables(conn, get_zip_state_mapping_path())
                    row_count = conn.execute("SELECT COUNT(*) FROM zip_rows").fetchone()[0]
                    if row_count == 0:
                        print(f"  No rows in {os.path.basename(db_path)}. Skipping export.")
                        conn.close()
                        continue
                    if scope_selected == "zip":
                        result = export_zip_detail_duckdb(conn, output_path, level, year, mapping_path=get_zip_state_mapping_path())
                    else:
                        result = export_zip_total_duckdb(conn, output_path, level, year)
                    conn.close()
                    zip_results.append(result)
                    duckdb_files_to_delete.append(db_path)
                    continue
                codes = load_industry_codes(int(level))
                if not codes:
                    print(f"  No NAICS codes found for level {level}. Skipping.")
                    continue
                conn = get_duckdb_conn(db_path)
                ensure_duckdb_zip_tables(conn, get_zip_state_mapping_path())
                loaded_codes = {row[0] for row in conn.execute("SELECT code FROM loaded_codes").fetchall()}
                if failed_by_code:
                    failed_by_code = {code: row for code, row in failed_by_code.items() if code not in loaded_codes}
                    write_failed_codes(failed_log_path, failed_by_code)
                retryable_codes = [code for code, row in failed_by_code.items() if str(row.get('retryable', '')).lower() == 'true']
                codes_to_run = codes
                if args.retry_failed:
                    if retryable_codes:
                        retryable_set = set(retryable_codes)
                        codes_to_run = [code for code in codes if code in retryable_set]
                        print(f"  Retrying {len(codes_to_run)} failed NAICS codes from {os.path.basename(failed_log_path)}.")
                    else:
                        print(f"  No retryable failed codes found in {os.path.basename(failed_log_path)}. Proceeding with full NAICS list.")
                run_start = datetime.now()
                max_run_seconds = max(1, args.zip_max_minutes) * 60
                batch_seconds = max(1, args.zip_batch_minutes) * 60
                processed_in_run = 0
                total_loaded = len(loaded_codes)
                total_codes = len(codes_to_run)
                completed_in_list = sum(1 for code in codes_to_run if code in loaded_codes)
                for code in codes_to_run:
                    if code in loaded_codes:
                        continue
                    try:
                        data, naics_field = fetch_zip_data(year, zip_dataset, args.api_key, use_indlevel=False, naics_filter=code)
                        df = build_zip_df(data, naics_field)
                        conn.register('batch_df', df)
                        conn.execute("INSERT INTO zip_rows SELECT * FROM batch_df")
                        conn.execute("INSERT INTO loaded_codes VALUES (?)", [code])
                        conn.unregister('batch_df')
                        loaded_codes.add(code)
                        processed_in_run += 1
                        total_loaded += 1
                        completed_in_list += 1
                        if code in failed_by_code:
                            failed_by_code.pop(code, None)
                    except Exception as e:
                        retryable = is_retryable_error(e)
                        detail = str(e).replace('\n', ' ').strip()
                        failed_by_code[code] = {
                            'code': code,
                            'reason': 'connection' if retryable else 'other',
                            'detail': detail[:500],
                            'retryable': str(retryable),
                            'last_attempt': datetime.now().isoformat()
                        }
                        write_failed_codes(failed_log_path, failed_by_code)
                        print(f"  Warning: failed NAICS {code} for year {year}: {e}")
                    elapsed = (datetime.now() - run_start).total_seconds()
                    if args.zip_batch_size and processed_in_run >= args.zip_batch_size:
                        print(f"  Batch checkpoint: processed {processed_in_run} codes this run ({total_loaded}/{total_codes} total).")
                        processed_in_run = 0
                    if elapsed >= batch_seconds:
                        print(f"  Progress: {completed_in_list}/{total_codes} codes completed for level {level}.")
                        run_start = datetime.now()
                    if (datetime.now() - start_time).total_seconds() >= max_run_seconds:
                        print(f"  Reached max run time ({args.zip_max_minutes} min). Resume by re-running.")
                        break
                write_failed_codes(failed_log_path, failed_by_code)
                if failed_by_code:
                    print(f"  Failed NAICS codes logged to {os.path.basename(failed_log_path)}. Retry with --retry-failed.")
                if scope_selected == "zip":
                    result = export_zip_detail_duckdb(conn, output_path, level, year, mapping_path=get_zip_state_mapping_path())
                else:
                    result = export_zip_total_duckdb(conn, output_path, level, year)
                conn.close()
                zip_results.append(result)
                duckdb_files_to_delete.append(db_path)
                continue
            if scope_selected == "zip":
                result = write_zip_detail(level_df, level, year, output_path)
            else:
                result = write_zip_total(level_df, level, year, output_path)
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
        results_file = f'{output_path}/results-{scope_folder}.md'

        if scope_selected == "zip":
            files_section = "Sent to state folders.\n"
        else:
            files_section = ""
            for result in zip_results:
                file_size_formatted = format_size(result['file_size'])
                files_section += f"- **Level {result['level']}**: `{result['filename']}` - {result['rows']:,} rows, {file_size_formatted}\n"

        scope_arg = f" --scope {scope_selected}"
        if args.naics_level.lower() == 'all':
            command_used = f"python annual.py {year}{scope_arg} --output-path {output_path}"
        else:
            command_used = f"python annual.py {year}{scope_arg} --naics-level {args.naics_level} --output-path {output_path}"

        if scope_selected == "zip":
            state_map = load_zip_state_map()
            state_count = len(state_map['State'].unique()) if state_map is not None else 1
            total_files_report = (state_count + 1) * len(zip_results) * (len(effective_years) if len(effective_years) > 1 else 1)
        else:
            total_files_report = len(zip_results) * (len(effective_years) if len(effective_years) > 1 else 1)
        results_title = "Results - Zipcodes Detail" if scope_selected == "zip" else "Results - Zipcodes Aggregated Metrics"
        columns_block = "- Zip (zipcode)\n- Naics (NAICS code at specified level)\n- Establishments (total)\n- Employees (total)\n- Payroll (total)"
        if scope_selected == "ziptotal":
            columns_block = "- Zip (zipcode)\n- Industries (unique count at specified NAICS level)\n- Establishments (total)\n- Employees (total)\n- Payroll (total)"

        filename_convention = f"US-<STATE>-zipcodes-naics<level>-<year>.csv" if scope_selected == "zip" else f"zipcodes-naics<level>-<year>.csv"
        results_content = f"""# {results_title}

**Last successful completion:** {end_time_str}

## Execution Timeline

- **Start time:** {start_time_str}
- **End time:** {end_time_str}
- **Total run time:** {duration_str}

## Output Details

- **Number of files generated:** {total_files_report}
- **NAICS levels processed:** {', '.join([r['level'] for r in zip_results])}
- **Census years:** {census_years_str}
- **Total output size:** {total_size_formatted}

### Generated Files

{files_section}

## Generation Details

- **Generated by:** `{os.path.basename(script_location)}`
- **Script location:** `{script_location}`
- **Command:** `{command_used}`

## Data Summary

Each output file contains zipcode metrics with the following columns:
{columns_block}

**File Naming Convention:**
```
{filename_convention}
```
"""

        with open(results_file, 'w') as f:
            f.write(results_content)

        print(f"\nResults saved to: {results_file}")
        print(f"Completed: {end_time_str}")
        print(f"Total run time: {duration_str}")
        print(f"Total files generated: {len(zip_results)}")
        if duckdb_files_to_delete:
            should_prompt = sys.stdin.isatty() and not args.delete_duckdb
            should_delete = args.delete_duckdb
            if should_prompt:
                prompt = f"If the output looks correct, delete DuckDB files for {year} now? [y/N]: "
                response = input(prompt).strip().lower()
                should_delete = response in ['y', 'yes']
            if should_delete:
                for db_path in sorted(set(duckdb_files_to_delete)):
                    if not os.path.basename(db_path).startswith(f'zip-pre2017-{year}-'):
                        continue
                    try:
                        os.remove(db_path)
                        print(f"Deleted {os.path.basename(db_path)}")
                    except OSError as exc:
                        print(f"Unable to delete {db_path}: {exc}")
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

        processed_df = process_county_data(raw_df, year, drop_fips=(scope_selected == "state"))

        if processed_df is None or processed_df.empty:
            print(f"  No data after processing for {state_code}")
            continue

        state_results = {'state': state_code, 'files': []}

        if scope_selected == "country":
            state_df = processed_df.copy()
            state_df['Fips'] = f"{int(fips):02d}"
            for level in levels_to_process:
                level_df = filter_by_naics_level(state_df, level)
                if level_df.empty:
                    continue
                grouped = level_df.groupby(['Fips', 'Naics'], as_index=False)[['Establishments', 'Employees', 'Payroll']].sum()
                country_level_frames[level].append(grouped)
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
    states_processed = len(state_fips) if scope_selected in ["county", "state", "country"] else len(all_results)
    total_files_report = total_files * (len(effective_years) if len(effective_years) > 1 else 1)
    columns_block = "- Naics (NAICS code at specified level)\n- Establishments (number of establishments)\n- Employees (total employees)\n- Payroll (total annual payroll in $1000s)"
    if scope_selected != "state":
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
- **Total files generated:** {total_files_report}
- **NAICS levels processed:** {', '.join([str(l) for l in levels_to_process])}
- **Census years:** {census_years_str}
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

def zip_years_for_scope(scope_selected, years, scopes):
    if scope_selected not in ["zip", "ziptotal"]:
        return years
    if 'all' not in scopes:
        return years
    years_int = [int(y) for y in years]
    has_2017_plus = any(y >= 2017 for y in years_int)
    if has_2017_plus:
        return [str(y) for y in years_int if y >= 2017]
    return [str(y) for y in years_int]

for scope_selected in scope_list:
    effective_years = zip_years_for_scope(scope_selected, year_list, scope_list)
    for raw_year in effective_years:
        year = int(raw_year)
        args.year = str(year)
        run_scope(year, scope_selected, effective_years)
