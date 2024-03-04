[Data Pipeline](../../)

# Process Industries

For States, Counties and Zip Codes

TO DO: Send 50 state files to /community-data/industries/naics/US/country

### NAICS Zip Code data

Starting with 2019, [ZIP Codes Business Patterns (ZBP)](https://www.census.gov/data/developers/data-sets/cbp-zbp/zbp-api.html) are available in the County Business Patterns (CBP) API which we also use for state and county naics processing.  [Process zips code zcta prior to 2019](/community-data/process/naics/)


### County Business Patterns (CBP)

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
Country2 + State2 - census - naics[2,4,6] - [counties,zip] - year

We'll need new annual US files. Previous:
[US-census-naics6-2020.csv](/community-data/industries/naics/US/country/US-2021-Q1-naics-6-digits.csv)

Examples:<!-- 
With Fips (5-digit state and county) 
US36005-census-naics6-2020.csv for a single county. Not needed currently. -->
[USAK-census-naics6-2020.csv](/community-data/us/state-naics-update/AK/USAK-census-naics6-2020.csv)
[USAK-census-naics6-counties-2020.csv](/community-data/us/state-naics-update/AK/USAK-census-naics6-counties-2020.csv)

**Columns**
- Fips - Only in counties files.
- Naics - ActivityProducedBy (6-digit naics)  
- Establishments - Other (Number of Extablishments)  
- Employees - Employment FlowAmount (Number of Employees)  
- Payroll - US Dollars (Annual Wages)
<!--
- Population - Included with our [Machine Learning](/machine-learning/) output
- Sqkm or Sqmiles - To be added
-->

**For Industry Comparisons**

We send the annual naics files to: /community-data/industries/naics/us/counties-update/
Following local review, we manually move to: [/community-data/industries/naics/us/counties/](/community-data/industries/naics/us/counties/)

For each year, there are 3 for the US, and 6 for each state:  

US/country/US-census-naics2-2023.csv
US/country/US-census-naics4-2023.csv
US/country/US-census-naics6-2023.csv

US/counties/NY/US-NY-census-naics2-2023.csv
US/counties/NY/US-NY-census-naics4-2023.csv
US/counties/NY/US-NY-census-naics6-2023.csv
US/counties/NY/US-NY-census-naics2-counties-2023.csv
US/counties/NY/US-NY-census-naics4-counties-2023.csv
US/counties/NY/US-NY-census-naics6-counties-2023.csv

<!--
Here are the 4 year old files we're eliminating:
https://github.com/ModelEarth/community-data/tree/master/us/state/NY
NY is 75K with no counties, 836K with counties.

**For Timelines**

We send the year files here:
/community-data/timelines/naics/us/

For timeline projections, we just use naics6 (2017 to 2023).
With and without country rows for each state.

/community-data/timelines/naics/us/ALL/US-census-naics6-2017.csv
/community-data/timelines/naics/us/NY/USNY-census-naics6-2017.csv
/community-data/timelines/naics/us/NY/USNY-census-naics6-counties-2017.csv

So for 2017 to 2023 there are 7 year files for the US with naics6, 
and 14 year files for each state with naics6.
-->

**PIPELINE**

Python pulls from the [US Census CBP&nbsp;API](https://www.census.gov/data/developers/data-sets.html).

The Jupyter Notebook for industry data preparation resides in [naics-annual.ipynb](naics-annual.ipynb).

In your webroot, create a virtual environment and install libraries.
Using the root will allow you to send output to the community-data repo.

	python3 -m venv env &&
	source env/bin/activate &&
	pip install pandas  &&
	pip install tqdm

Avoid pip3 in virtual environments.


<!-- Added steps here to avoid 500 error.
This error also occured when not in virtual env.
 -->
Run if you've previously encountered [500: Internal Server Error](https://stackoverflow.com/questions/36851746/jupyter-notebook-500-internal-server-error)

This can also give you a newer Juyter interface:

	pip install notebook &&
	pip install --upgrade nbconvert

Open Jupyter Notebook with this command then click naics-annual.ipynb and run each step:
<!-- if this cd has 500 error again, remove the cd and stay launch jupyter in the root. -->

	cd data-pipeline/industries/naics &&
	jupyter-notebook

Or you can run [naics-annual.ipynb](process/python/naics-annual.ipynb) from the command line:  

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

	{base_url}/{year}/cbp?get={columns_to_select}&for=county:*&in=state:{fips:02d}

For example, to get the 2016 data for all counties in the state of Georgia, you can use the following URL:

	https://api.census.gov/data/2016/cbp?get=GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2012,NAICS2012_TTL,ESTAB,EMP,PAYANN&for=county:*&in=state:13

You can find a list of columns to select on [this link](https://api.census.gov/data/2016/cbp/variables.html).

### Note for the data used in the Bubblemap
If rounding off 8 decimals, ozone depletion, pesticides and a few others would need to be switched to scientific notation in the data file. This would allow the files to be reduced as follows:

US from 151kb to under 72.7kb
GA from 120kb, to under 59.2kb


