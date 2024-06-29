[Active Projects](../../projects/)

# ML for Community Forecasting Timelines

## Our RealityStream ML Forecasting Models

TO DO: [RealityStream](/RealityStream) - Logistic Regression, Random Forest and Support Vector Machines

<!--
[Industry Features for RealityStream Testing (Maine Naics2 Counties 2021)](https://github.com/ModelEarth/community-timelines/blob/main/training/naics2/US/counties/2021/US-ME-training-naics2-counties-2021.csv)
-->

TO DO: [UN Goal Timelines](/data-commons) - Pull timeline data files for each goal

TO DO: Create parameter-canopy.yaml with paths to [forest coverage data](/data-commons/docs/conservation/) to pass into [Run Models](/RealityStream/input/industries/) - Jing

TO DO: [Use Feed View](/feed/view/) to assemble parameters.yaml on-the-fly and pass as #parameters to our [Run Modles CoLab](/RealityStream/input/industries/).

<!--
ML Team: Sijia, Lily, Irene, Honglin, Ronan, Luwei, Wenxi, Magie (Haohao), Ivy
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
Training files are output to [community-timelines/training](https://github.com/ModelEarth/community-timelines/tree/main/training) by python/ML-bkup.ipynb from [Our CoLab on Google](https://colab.research.google.com/drive/1wmJ3V9eqD8KbmBiP-hLeSstwOUt5iS2V?usp=sharing)  


Our IDs for States and counties = Federal Information Processing Standard (FIPS)  
Our "geo" hash value appends the country to the front of FIPS.  
Example: US12345 (US state 12, county 345)

TO DO: [Send industries data to Random Bits Forest](/RealityStream/input/industries/)

IN PROGRESS: [Update NAICS source files to include zip code data (ZTCA)](/data-pipeline/industries/naics/)


## Bees/Trees/Jobs/Income as Target Column (y=1)

We're using the state of Maine (ME) for our sample counties.  
We're using NAICS levels 2 and 4 in our training files.

- [Bee the Predictor](/RealityStream/input/bees/)
- [Tree Canopy Data](/data-pipeline/research/canopy/)

## Data Prep and Presentation

<!-- We could compare prior Random Forest with code in Run Modles. - Sijia -->

TO DO: Web page displaying US counties at risk of increased poverty - Use Google Data Commons API for FIPS county poverty target data and international target data. Pull with an [Observable Data Loader](../../../timelines/observable/)

TO DO: Find equivalent county data for India and China (Country Census or Google Data Commons)

TO DO: Web page displaying Industries that predict improving and declining [bee populations](../../../research/bees/) - Irene

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

## Facebook Prophet

TO DO: Pull [industry timeline data for all states](https://github.com/ModelEarth/community-timelines/) into our [Facebook Prophet Streamlit fork](https://github.com/modelearth/prophet). Test with one state first.

Upload time series dataset to train, evaluate and optimize forecasting models in a few clicks. In addition to the Streamlit repo, look for option in the following Facebook tools.

[Learn more at facebook.github.io/prophet](https://facebook.github.io/prophet/)
Prophet is robust to outliers, missing data, and dramatic time series changes
Prophet works best with time series that have strong seasonal effects.


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