[Data Pipeline](../../)

<a href="../../../data-pipeline/admin/#node=naics" class="btn btn-success" style="float:right; display:inline-block;">
    Process Data
</a>

# Annual NAICS Pull

### County and Zip Business Patterns (CBP)<br>Zip Business Patterns (ZBP) - Pre-2019

  - Pre‑2017 requires NAICS-specific pulls (using DuckDB batching) because INDLEVEL (naics 2 to 6) was not available yet.
  - Pre-2019 Requires ZBP for ZIP scope.

Generates annual .csv files for [Community Datasets](http://model.earth/community-data/) of zip code, county, state, US  aggregates (country) for [industries by location](../../../localsite/info/).

- [Zip](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/zip)<!-- Also [Zip code data processing](https://model.earth/community-zipcodes/)-->
- [County](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/county)
- [States](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/state)
- [Country (sums)](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/country)

**Columns**
- Fips or Zip - State in 2-digit FIPS, County is 5-digit FIPS.
- Industries - Count of unique naics categories (no Naics column when present)
- Naics - North American Industry Category ID (2, 4 & 6 digits)  
- Establishments - Number of Extablishments  
- Employees - Employment FlowAmount (Number of Employees)  
- Payroll - US Dollars (Annual Wages)
<!--
- Population - Included with our [Machine Learning](/machine-learning/) output
- Sqkm or Sqmiles - To be added
-->

## Setup

For each run, change the scope.selected in config.yaml - <a href="../../../data-pipeline/admin/#node=naics">Admin Interface</a>

```bash
# Create and activate virtual environment
python3 -m venv env
source env/bin/activate

python -m pip install --upgrade pip
pip install "numpy<2" pandas pyarrow requests pyyaml

python annual.py
```

### Scopes

`annual.py` supports multiple scopes. Use `--scope` to override config:

```bash
python annual.py --scope county
python annual.py --scope state,country
python annual.py --scope all
```

### Config

`annual.py` reads defaults from `config.yaml` when CLI params are not provided. CLI args always override config values.

Config keys:
- `YEAR`: Census data year (default 2021 if not set)
- `NAICS_LEVEL`: `all` or a single level (`2`, `4`, `6`)
- `STATE`: Optional two-letter state code (e.g., `GA`)
- `OUTPUT_PATH`: Output directory
- `API_KEY`: Optional Census API key (only needed for higher rate limits)
- `SCOPE.selected`: One or more scopes (`zip`, `zip-totals`, `county`, `county-totals`, `state`, `country`, or `all`). Comma-separated for multiple (e.g., `county,state`).

Local state FIPS file: `state-fips.csv`

CBP year availability: 2023 is the latest published year; 2024 is expected in summer 2026.

Example (config-only):
```bash
python annual.py 2023 --naics-level all --scope all
```

Example (override a single value):
```bash
python annual.py 2022 --naics-level 6 --scope state --state GA
```


"The Business Patterns series covers most of the country’s economic activity, but excludes data on self-employed individuals, employees of private households, railroad employees, agricultural production employees, and most government employees."

State-county-naics files previouly resided in [us/state](https://github.com/modelearth/community-data/tree/master/us/state) <span class="local" style="display:none">- <a href="../../../us/state">view on localhost</a></span>

USEPA has these 2 crosswalks. (There are no naics industry titles in these.)

- [2017 NAICS to 2017 BEA](https://github.com/USEPA/flowsa/blob/master/flowsa/data/NAICS_to_BEA_Crosswalk_2017.csv)
- [Timeseries of NAICS codes for 2002, 2007, 2012, 2017](https://github.com/USEPA/flowsa/blob/master/flowsa/data/NAICS_Crosswalk_TimeSeries.csv)

Titles might need to be pulled from separate files (2017 and 2022) using the XLSX files downloadable from the following census page. Click "downloadable files" at [census.gov/naics/?48967](https://www.census.gov/naics/?48967) &nbsp;The 2017 and 2022 files can reside in [community-data/us](https://github.com/ModelEarth/community-data/tree/master/us).

<!--
TO DO: Locate crosswalk relating North American NAICS, European Union NACE codes, and any other trade crosswalks.

TO DO: Generate files with a GitHub Action - [Github&nbsp;Actions&nbsp;samples](https://model.earth/community/projects/#pipeline) 

[New NAICS columns](/community-data/industries/naics/US/country/US-2021-Q1-naics-6-digits.csv) used by [upcoming naics list](/localsite/info/#state=GA&beta=true).

Old 2012 6-digit Naics
https://github.com/modelearth/localsite/blob/main/info/naics/lookup/6-digit_2012_Codes.csv
-->

**File Name**
US - naics[2,4,6] - <scope> - year

We'll need new annual US files. Previous:
[US-naics6-country-2020.csv](/community-data/industries/naics/US/country/US-naics6-country-2020.csv)

**NAICS Level 2 Range Legend (ZIP scope)**
- 31 Manufacturing (31-33)
- 44 Retail Trade (44-45)
- 48 Transportation and Warehousing (48-49)
- 92 Public Administration (Not available for naics 2 level zip codes)

For ZIP scope NAICS level 2 outputs, range codes are saved as the starting code (31-33 -> 31, 44-45 -> 44, 48-49 -> 48).

Examples:<!-- 
With Fips (5-digit state and county) 
US36005-naics6-county-2020.csv for a single county. Not needed currently. -->
[USAK-naics6-state-2020.csv](/community-data/us/state-naics-update/AK/USAK-naics6-state-2020.csv)
[USAK-naics6-county-2020.csv](/community-data/us/state-naics-update/AK/USAK-naics6-county-2020.csv)


<!--
Here are the 4 year old files we're eliminating:
https://github.com/ModelEarth/community-data/tree/master/us/state/NY
NY is 75K with no counties, 836K with counties.

**For Timelines**

We send the year files here:
/community-data/timelines/naics/us/

For timeline projections, we just use naics6 (2017 to 2023).
With and without country rows for each state.

/community-data/timelines/naics/us/ALL/US-naics6-country-2017.csv
/community-data/timelines/naics/us/NY/USNY-naics6-state-2017.csv
/community-data/timelines/naics/us/NY/USNY-naics6-county-2017.csv

So for 2017 to 2023 there are 7 year files for the US with naics6, 
and 14 year files for each state with naics6.
-->

**PIPELINE**

Python pulls from the [US Census CBP&nbsp;API](https://www.census.gov/data/developers/data-sets.html).

The Jupyter Notebook for industry data preparation resides in [naics-annual.ipynb](naics-annual.ipynb).

We use naics-annual.ipynb to generate country, state and county files.
Zip code file generation resides in [community-zipcodes](/community-zipcodes/).

In your webroot, create a virtual environment and install libraries.
Using the root will allow you to send output to the community-data repo.

  python3 -m venv env
  source env/bin/activate
  pip install pandas  &&
  pip install tqdm

Avoid pip3 in virtual environments.

To run new cmds in the same virtual environment, in a new terminal run:

  source env/bin/activate

In Windows run:

  \env\Scripts\activate.bat

Run if you've previously encountered [500: Internal Server Error](https://stackoverflow.com/questions/36851746/jupyter-notebook-500-internal-server-error)

If your verion of Conda is old, this will give you a newer Jupyter interface:

  pip install notebook &&
  pip install --upgrade nbconvert

Open Jupyter Notebook with this command then click naics-annual.ipynb and run each step:
<!-- if this cmd has 500 error again, remove the cd line and launch jupyter in the root. -->

  cd data-pipeline/industries/naics &&
  jupyter-notebook

Or you can run [naics-annual.ipynb](naics-annual.ipynb) from the command line:  

  cd data-pipeline/industries/naics &&
  jupyter nbconvert --to notebook --inplace --execute naics-annual.ipynb


<!--
Timeout still occured with the following...
Change the timeout (sleep) on your computer. Changed Start Screen Saver when inactive from 20 minutes to never.
-->

Only takes about 10 minutes to run through the steps to generate a year.

After running, you can delete the data_raw folder
<!-- county_level folder inside data_raw\BEA_Industry_Factors. -->

The last block of this notebook contains the code for generating the state-wide data. Getting the state-wide totals directly from the Census API results in numbers different from the sum of each state’s county totals since the cesus excludes payroll and number of employees for counties with only a couple firms.  



## Usage  

Resulting data is used within the upcoming [industry comparison](/localsite/info/) page to load industries for counties.

### Data Includes US Industries by County

Annual Payroll, Employee Count, Establishments (with estimates filling gaps that protect anonymity)  

Currently years 2012 to 2020 work.

The last block of this notebook contains the code for generating the state-wide data. When only 1 or 2 of an industry reside in a county, numbers are omitted by the US Census to protect privacy. As a result, the state-wide totals from the Census API are larger than the sum of each state’s county totals.

[Additional info](https://github.com/modelearth/community/issues/9)

After aggregating the data, you can delete the folders inside bea/data_raw/BEA\_Industry\_Factors/county\_level and state\_level.



### API calls

As included in the [naics-annual.ipynb](naics-annual.ipynb) notebook, the base url for API calls is:

  https://api.census.gov/data

A full URL follows the following format:

<div>{base_url}/{year}/cbp?get={columns_to_select}&for=county:*&in=state:{fips:02d}</div>

For example, to get the 2016 data for all counties in the state of Georgia, you can use the following URL:

  https://api.census.gov/data/2016/cbp?get=GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2012,NAICS2012_TTL,ESTAB,EMP,PAYANN&for=county:*&in=state:13

You can find a list of columns to select on [this link](https://api.census.gov/data/2016/cbp/variables.html).

### Note for the data used in the Bubblemap
If rounding off 8 decimals, ozone depletion, pesticides and a few others would need to be switched to scientific notation in the data file. This would allow the files to be reduced as follows:

US from 151kb to under 72.7kb
GA from 120kb, to under 59.2kb

## Zip Scope (ZBP/CBP)

The ZIP scope is also handled by `annual.py` and uses the Census ZBP API through 2016, and the CBP API for 2017+ (previously switched at 2019).

pre‑2017, to get industry data for zip codes requires pulling each NAICS individually. industry_id_list.csv provides a list of available naics IDs. (Maybe lists for each naics level will be used later. The list does not need and index or decimal on the naics value.)

DuckDB is used for our pre-2017 zip codes naics pull (split by state) because DuckDB is more efficient than pandas for large multi-year ZIP workloads due to lower memory usage and faster aggregations on big datasets.

- 2016 zip scope (state folders) took over 20 minutes.
- 2023 zip scope (state folders) took 4 minutes.

Outputs:
- `US-<STATE>-naics<level>-zip-<year>.csv` (state subfolders)
- `results-zips.md`

Notes:
- For ZIP outputs, `Payroll` is 0 for all levels except NAICS 2.
- `Industries` appears only in the `ziptotal` scope and is the count of unique NAICS codes per ZIP at the selected level (not a single NAICS value).
- Pre‑2017 ZIP pulls use `industry_id_list.csv` to query by NAICS code. There may be better, newer sources than this legacy list.
- DuckDB is used for pre‑2017 ZIP batching to aggregate large ZIP datasets with lower memory use than pandas.
- Use `--zip-export-only` to rebuild state folders from existing DuckDB files without refetching.
- Use `--delete-duckdb` to delete pre‑2017 ZIP DuckDB files after a successful export (skips prompt).
- If `scope=all` and any years are 2017+, ZIP scope skips pre‑2017 years. If all years are pre‑2017, ZIP runs them.
