[Timelines ML](../../)

# NAICS Training Data for ML

North American Industry Classification System (NAICS)
We're creating a new Random Forest process informed [by the prior zip code zcta process](../../prep/all)

<!--
Our ML Group - Sijia, Kargil, Alison, Irene, Honglin, Ronan, Lily, Luwei, Wenxi, Magie and more.
-->

Two data structures are generated from our [community-data industry source files](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US).

TO DO: Update source files to pull generate zip code data (ZTCA)

### Our FIPS Rows for Training (one file per year)
Training files are output to [community-timelines/training](https://github.com/ModelEarth/community-timelines/tree/main/training) by python/ML-bkup.ipynb from [Our CoLab on Google](https://colab.research.google.com/drive/1wmJ3V9eqD8KbmBiP-hLeSstwOUt5iS2V?usp=sharing)

### Our Year Rows for Timelines (years 2017 to 2021)
Establishments, Employees, Payroll

Timeline files are output to [community-timelines/industries](https://github.com/ModelEarth/community-timelines/tree/main/industries) by [naics-timelines.py](../../prep/industries/) - Ronan

---

### Our Streamlit Forecasting ML Apps
- [Facebook Prophet](https://github.com/ModelEarth/prophet/) - Upload time series dataset to train, evaluate and optimize forecasting models in a few clicks.
- [RealityStream](https://github.com/ModelEarth/RealityStream) - Logistic Regression, Random Forest and Support Vector Machines

TO DO: Genearte RealityStream's original output for Job descriptions, add link in RealityStream repo.
TO DO: Document how non-coders can contribute to our [Data-Commons](/data-commons/) repo using [ObservableHQ.com](https://ObservableHQ.com)
TO DO: Apply target to FIPS on-the-fly with Javascript and [bee data from Irene](/data-pipeline/research/bees/)
TO DO: Apply target to FIPS using your [goal data](/data-commons/dist/) in our [Observable Data Commons](/data-commons/).


[Learn more at facebook.github.io/prophet](https://facebook.github.io/prophet/)
Prophet is robust to outliers, missing data, and dramatic time series changes
Prophet works best with time series that have strong seasonal effects.


<div style="background:#fff; padding:20px; max-width:1000px">
  <img src="input_format.png" style="width:100%;"><br>
</div>

## Bee/Tree/Poverty as Target Column (y=1)

We're using the state of Maine (ME) for our sample counties.  
We're using NAICS levels 2 and 4 in our training files.

- [Bee the Predictor](/data-pipeline/research/bees/) - with [TensorFlow Javascript](https://www.tensorflow.org/js/demos) - Irene
- [Tree Canopy Data](/data-pipeline/research/canopy/)

## Data Prep and Presentation

TO DO (Sijia): Random Forest forecasting. - Sijia will copy our prior .py file into a CoLab. We will update it for both FIPS and ZCTA.

TO DO: Web page displaying US counties at risk of increased poverty - Use Google Data Commons API for FIPS county poverty target data and international target data. Pull with an [Observable Data Loader](../../../timelines/observable/)

TO DO: Find equivalent coounty data for India and China (Country Census or Google Data Commons)

TO DO: Web page displaying Industries that predict improving and declining [bee populations](../../../research/bees/)

TO DO: Web page displaying Top ten Maine counties likely to have [declining tree canopy](/data-pipeline/research/canopy/) - Find a data source (county or zip)

TO DO: Use [Tensorflow.org](https://www.tensorflow.org/js/demos) for [Neural Network predictions](https://www.tensorflow.org/s/results/?q=neural%20networks) with our training data.

<!--
### Javascript Display in Tabulator

In javascript, we'll populate "Density" for each county and append it as a column in Tabulator. [Tabulator work in progress](/data-pipeline/timelines/tabulator/).

Density = Population / Km2

Density can also be thought of as PopPerKm2 (divided by 1000)
100,000 people living in an 80 Km2 county = 1250 people per Km2 = Density of 1.25
When displaying, we will multiply Density and Population by 1000.
-->

TO DO: County demographic attributes can be fetched from the Google Data Commons API for population, education levels, income/poverty levels.

Append 0 or 1 to the "y" column. Prior y column in community forecasting: y=1 when the current year’s poverty had no decline from the prior year AND the next year’s poverty increased by 2% or more.

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


## Recent Projects

### Prepare Python that loads naics data into Pandas for 2017 to 2021 for Maine

DONE - Project Contacts: Yanqing (Lily) and Sijia

Source files. Load these directly from the URL into Pandas.

https://model.earth/community-data/industries/naics/US/counties/ME/US-ME-census-naics4-counties-2021.csv

View source files on GitHub: [industries/naics/US/counties/ME](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/counties/ME)

---


### Output Timeline Files

DONE - CoLab link at the top of this page. Project Contact: Ronan

Output: One row per location (county) with columns for all naics4 industries with 3 attributes.

[prep/industries](../../prep/industries/)

<!--
Attributes:
Industry's Establishments per 1000 people
Industry's Employees per 1000 people
Industry's Average pay per Employee

Python library pulls the county population by year.
Let's also include the value of the center latitude and longitude.
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


Fips, N1111-Firms, N1111-People, N1111-Pay, N2222-Firms, N2222-People, N2222-Pay, ...

The following attribute names are equivalent:

Firms = Establishments
People = Employees
Pay = Payroll
-->

As a reference, the prior structure for zcta (zip code) training data was:
Zcta, JobsTotal, JobsAgriculture, JobsEntertainment, Population, Poverty, PovertyUnder18, Education, WorkExperience, y


---
<br>

### Display results of Random Forest

Sample from prior zcta process: