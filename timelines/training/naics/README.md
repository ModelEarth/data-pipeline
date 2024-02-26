[Timelines ML](../../)

# Training Data for NAICS ML

We're creating a new Random Forest process infomed [by the prior ztca process](../../prep/all)

We'll use the state of Maine (MN) as our sample counties.  
We'll use NAICS level 2 which has about 72 industries.

Could we process the data entirely in Pandas rather then using SQLLite?


### 1.) Yanqing - Prepare Python that loads naics4 data into Pandas for 2017 to 2021 for Maine.

https://model.earth/community-data/industries/naics/US/counties/MN/US-MN-census-naics4-counties-2021.csv

---
<br>

### 2.) Output annual training files to:
output/2021/2021-naics2-counties.csv

The training file format will be:

FIPS, N1111, N2222, N333, N4444, N5555

Each row is a location. (FIPS = countyID)

This is the equivalent to the prior file (ztca = zipcode):

zcta, JobsTotal, JobsAgriculture, JobsEntertainment,…
Population, Poverty, PovertyUnder18, Education,WorkExperience, WorkingFulltime, WorkingFulltime_Poverty, y

Ronan is working on a similar pivot in [pep/industries](../../prep/industries/) for timelines, except the timeline rows are years.

---
<br>

### 3.)  Sijia - Append 0 or 1 to the last column.

Look at prior process to document aspects to predict.

We can use county demographic attributes like education and poverty.

Count demographic attributes would be fetched from Google Data Commons.

---
<br>

### 4.) Display results of Random Forest