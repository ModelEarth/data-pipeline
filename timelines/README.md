[Active Projects](../../projects/)

# Timelines for Forecasting

Our interface sends industry data as features to six popular ML models, including [Random Bits Forest](/RealityStream/input/industries/).

<!--
2024/2025 ML Team: Sijia, Lily, Irene, Honglin, Ronan, Luwei, Wenxi, Magie, Ivy, Aashish, Dinesh
-->

[Basic timelines](earthscape/) - [Earthscape tabulator](training/naics/) - [Tabulator directly](tabulator/)

## NAICS Data for Community Features

North American Industry Classification System (NAICS)
The following two datasets are generated from our [community-data naics files](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US).


### 1. Our Year Rows for Timelines (years 2017 to 2021)
Establishments, Employees, Payroll
Timeline files are output to [community-timelines/industries](https://github.com/ModelEarth/community-timelines/tree/main/industries) by [naics-timelines.py](prep/industries/) - By Ronan


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

### Display results of Random Forest

As a reference, the prior structure for zcta (zip code) training data was:
Zcta, JobsTotal, JobsAgriculture, JobsEntertainment, Population, Poverty, PovertyUnder18, Education, WorkExperience, y

Sample from prior zcta process:
-->

### 2. Our FIPS Location Rows for Training (one file per year)
Training files are output to [community-timelines/training](https://github.com/ModelEarth/community-timelines/tree/main/training) by [ML-bkup.ipynb](https://github.com/ModelEarth/data-pipeline/tree/main/timelines/training/naics/python) from [Our CoLab on Google](https://colab.research.google.com/drive/1wmJ3V9eqD8KbmBiP-hLeSstwOUt5iS2V?usp=sharing)  


Our IDs for States and counties = Federal Information Processing Standard (FIPS)  
Our "geo" hash value appends the country to the front of FIPS.  
Example: US12345 (US state 12, county 345)

IN PROGRESS: [Update NAICS source files to include zip code data (ZTCA)](/data-pipeline/industries/naics/)


## Bees/Trees/Jobs/Income as Target Column (y=1)

We're using the state of Maine (ME) for our sample counties.  
We're using NAICS levels 2 and 4 in our training files.

- [Bee the Predictor](/RealityStream/input/bees/)
- [Tree Canopy Data](/data-pipeline/research/canopy/)


<div style="background:#fff; padding:20px; max-width:1000px">
  <img src="img/input_format.png" style="width:100%;"><br>
</div>


## Recent Projects

[Review Training Data for ML (Tabulator)](training/naics/) - ML Team
[Random Forest Prep](prep/all/) - [RBF](/RealityStream/output/blinks/) - Sijia

[RealityStream - ML Classification Models](/RealityStream)
Targets: Jobs, Bees, Blinks, [Industries](/RealityStream/input/industries/)

[Tabulators using Javascript](tabulator/) - Rupesh
[Industries Timeline Data Prep](prep/industries/) - Ronan
[Observable Data Commons](/data-commons/dist/) - Everyone
[Observable Notes](observable/)

[SQLite in Browser](sqlite/phiresky/) from the phiresky timeline
[Image Generation](../research/stream/)


## ADD DATA SOURCES

[International Data from Google Data Commons API](../../../data-commons/)
[Worldbank Development Indicators](https://github.com/phiresky/world-development-indicators-sqlite/) - by phiresky

## Time Regression Examples

Time series regression is a statistical method for predicting a future response based on the response history (known as autoregressive dynamics) and the transfer of dynamics from relevant predictors.

[Community Forecasting - Zip Code Timelines](/community-forecasting/?page=zip/#zip=30318)
[Line Race](line-race.html) - [Line Stack](line-stack.html) - [Apache eChart](https://echarts.apache.org/examples/en/editor.html?c=line-race)

Regression is a statistical method that attempts to determine the strength and character of the relationship between one dependent variable (usually denoted by Y) and a series of other variables (known as independent variables).

[NAICS Tabulator Output](training/naics/)