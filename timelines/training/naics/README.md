[Timelines ML](../../)

# NAICS Training Data for ML

We're creating a new Random Forest process infomed [by the prior ztca process](../../prep/all)

We'll use the state of Maine (MN) for our sample counties.  
We'll use NAICS level 4 which has about 72 industries.

Yanqing (Lily) is working on #1 and #2 below.
Our ML Group: Sijia, Irene, Ronan, Lily, Luwei, Wenxi, Magie and more.

TO DO:

1.) Use Random Forest to make forecasting based on naics industry levels:
- Top ten Maine counties at risk of increased poverty - Use Google Data Commons API for county data
- Top ten Maine counties likely to have a decline in bee populations - Find a data source (county or zip)
- Top ten Maine counties likely to have a decline decline in tree canopy - Find a data source (county or zip)

2.) Generate Maine CSV file for our [StreamLit Image Generation](../../../research/stream/).
3.) Apply y=1 on-the-fly with Javascript and [Observable](../../observable/).
4.) Use [Tensorflow.org](https://www.tensorflow.org/js/demos) for [Neural Network predictions](https://www.tensorflow.org/s/results/?q=neural%20networks).


### 1. Prepare Python that loads naics4 data into Pandas for 2017 to 2021 for Maine

Project Lead: Yanqing (Lily)

Source files. Load these directly from the URL into Pandas.

https://model.earth/community-data/industries/naics/US/counties/MN/US-MN-census-naics4-counties-2021.csv

View files on GitHub: [industries/naics/US/counties/MN](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/counties/MN)

---


### 2. Output annual training files

Project Lead: Yanqing (Lily)

Save to: output/2021/2021-naics2-counties.csv
Later these will reside in /community-forecasting

To streamline reuse, we'll avoid creating a header row.

Each row is a location (Fips = countyID) with 73 industries, each with 3 attributes (224 columns total)

Industry's Establishments per 1000 people
Industry's Employees per 1000 people
Industry's Average pay per Employee

We'll need a Python library that pulls the county population by year.
Let's also include the value of the center latitude and longitude
We could include the county name, then see if the model predicts differently without it.

A file called columns.md could be output with a list of the column values:

Fips
Name
Population
Latitude
Longitude
Naics X Establishments per 1000
Naics X Employees per 1000
Naics X Average pay
[repeat]

<!--
Fips, N1111-Firms, N1111-People, N1111-Pay, N2222-Firms, N2222-People, N2222-Pay, ...

The following attribute names are equivalent:

Firms = Establishments
People = Employees
Pay = Payroll
-->

As a reference, the prior structure for ztca (zipcode) was:

zcta, JobsTotal, JobsAgriculture, JobsEntertainment,…
Population, Poverty, PovertyUnder18, Education,WorkExperience, WorkingFulltime, WorkingFulltime_Poverty, y

Ronan is working on a similar pivot in [prep/industries](../../prep/industries/) for timelines, except the timeline rows are years.

---

### 3. Append 0 or 1 to the last column.

County demographic attributes can be fetched from the Google Data Commons API for population, education levels, income/poverty levels.

Prior y column:
y=1 when the current year’s poverty had no decline from the prior year AND the next year’s poverty increased by 2% or more.
<!--
Applied in
prep/all/zcta_2016.SQL.txt

-- Change from prior year is steady (0%) or increasing, change to next year is increasing by 2% or more.

CASE
      WHEN (prior1.poverty - p.poverty) >= 0 AND (p.poverty - next.poverty) >= 2 THEN 1
      ELSE 0
END

AS y -- the povertyBinary for >= 2% in coming year, and no decline for current year.
-->

---
<br>

### 4.) Display results of Random Forest

Sample from prior zcta process: