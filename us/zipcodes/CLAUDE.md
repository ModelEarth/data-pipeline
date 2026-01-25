# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This directory contains Python scripts for fetching and processing U.S. Census Bureau Zip Code Business Patterns (ZBP) data. The scripts retrieve NAICS industry data by zipcode from the 2018 Census ZBP API and generate CSV files with establishment, employment, and payroll statistics.

## Common Commands

### Run the main zipcodes aggregation script
```bash
# Default: year 2018, industry level 6
python zipcodes.py

# Specify year
python zipcodes.py 2023

# Specify year and industry level
python zipcodes.py 2023 --ind-level 2
```
Generates `zipcodes-naics<ind_level>-<year>.csv` with aggregated metrics for all zipcodes at the specified industry level.

**Command-line parameters:**
- `year`: Census data year (positional argument, default: 2018)
- `--ind-level <level>`: Industry level 2-6 (default: 6)
- `--output-path <path>`: Output directory (default: us/zipcodes) - created automatically if doesn't exist

The script displays the absolute output path when run.

### Run zipcode processing (single or batch)
```bash
# Single zipcode mode
python zipcodes-naics.py --zipcode 98006 --ind-level 2

# Batch mode with custom range
python zipcodes-naics.py --batch-start 0 --batch-end 1000 --ind-level 2

# Custom year and output path
python zipcodes-naics.py --zipcode 98006 --year 2019 --output-path ../../../community-data/US/zip

# Default batch mode (indices 3000-3500, year 2018, outputs to ../../../community-data/US/zip)
python zipcodes-naics.py
```
Fetches data and creates nested directory structure: `<output-path>/X/X/X/X/X/zipcode-<XXXXX>-census-naics<level>-<year>.csv`

**Command-line parameters:**
- `--zipcode <code>`: Single zipcode to process
- `--batch-start <n>`: Starting index for batch mode
- `--batch-end <n>`: Ending index for batch mode
- `--ind-level <level>`: Industry level 2-6 (default: 2)
- `--year <year>`: Census data year (default: 2018)
- `--output-path <path>`: Output directory (default: ../../../community-data/US/zip) - created automatically if doesn't exist

The script displays the absolute output path when run.

### Virtual Environment Setup
```bash
python3 -m venv env
source env/bin/activate  # On macOS/Linux
pip install pandas requests
```

## Architecture

### Data Source
All scripts fetch from the Census Bureau ZBP API:
```
https://api.census.gov/data/<year>/zbp?get=ZIPCODE,NAICS2017,ESTAB,EMPSZES,PAYANN&for=&INDLEVEL=<level>
```

Parameters:
- `year`: Census data year (configurable via --year, default: 2018)
- `INDLEVEL`: Industry aggregation level (2, 3, 4, 5, 6)
  - Level 2: 2-digit NAICS codes (broadest)
  - Level 6: 6-digit NAICS codes (most granular)

### Script Purposes

**zipcodes.py** - Aggregate metrics generator
- Fetches all data for a given industry level and year
- Groups by zipcode to calculate:
  - Unique industry count
  - Total establishments
  - Total employees
  - Total payroll
- Outputs single CSV: `zipcodes-naics<level>-<year>.csv`
- Configurable year (positional argument), industry level, and output path
- Use case: High-level zipcode comparisons

**zipcodes-naics.py** - Zipcode processor (single or batch mode)
- **Single mode**: `--zipcode <code>` processes one zipcode efficiently
- **Batch mode**: `--batch-start` and `--batch-end` process zipcode ranges
- Configurable year (`--year`) and output path (`--output-path`)
- Default output: `../../../community-data/US/zip` (configurable)
- Creates nested 5-level directory structure based on zipcode digits
- Outputs detailed NAICS data per zipcode
- Use case: Populating directory structure with granular data

### Data Flow Pattern

1. API request returns JSON with all zipcodes for an industry level
2. Data is temporarily saved to `ind_data.json`
3. Pandas DataFrame loads and processes JSON
4. Output varies by script:
   - `zipcodes.py`: Aggregates and exports single CSV
   - `zipcodes-naics.py`: Filters by zipcode and exports to nested directories

### Directory Structure Convention

For zipcode-specific files, creates nested structure:
```
<output-path>/1/2/3/4/5/zipcode-12345-census-naics<level>-<year>.csv
```
- Default output-path: `../../../community-data/US/zip`
- Each directory level represents one digit of the 5-digit zipcode
- Year is configurable via `--year` parameter

## Results Files

Both scripts automatically generate markdown result files documenting successful completions:

**results.md** (from zipcodes.py):
- Start time, end time, and total run time
- Number of rows in aggregated output
- Total output file size (excludes naics subfolder)
- Industry level and census year
- Script location and command used

**results-naics.md** (from zipcodes-naics.py):
- Start time, end time, and total run time
- Number of zipcodes processed
- Total rows written across all files
- Total output file size
- Processing mode (single vs batch)
- Script location and command used

## Consolidation Notes

**Completed consolidation:**
- Former `single_zipcode.py` functionality has been integrated into `zipcodes-naics.py` (formerly `split_zip_data.py`)
- Use command-line arguments for flexible data processing:
  - `--zipcode <code>`: Single zipcode processing
  - `--batch-start <n> --batch-end <m>`: Batch processing
  - `--ind-level <level>`: Specify industry level (2-6, default: 2)
  - `--year <year>`: Specify Census data year (default: 2018)
  - `--output-path <path>`: Specify output directory (default: ../../../community-data/US/zip)
- Shared directory creation logic eliminates code duplication
- The inefficient single_zipcode.py script has been removed
