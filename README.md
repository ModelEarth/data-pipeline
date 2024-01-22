[Community Data](/community-data/)
# Model.Earth Data Pipeline

GitHub: [Data-Pipeline](https://github.com/modelearth/data-pipeline)  
The data pipeline formats NAICS files by county and zip for [Industry Impact Pages](https://model.earth/localsite/info/)  

**TO DO:**

Use the following [examples of Merging Input-Output Data for Totals](/localsite/info/data/totals/) to show actual dollar values in the US EPA [inflow-outflow chart](../../../io/charts/). Here's a stand-alone [widget for testing](http://localhost:8887/io/build/iochart.html#indicators=ENRG,GHG,VADD&sectors=113000,327310,327400,333613,335912,336111,562111,562212)

[WebStorm Notes](https://docs.google.com/document/d/1BKxx5Q5rtNgZ9cD-Hsgdi_nEL1YPCfPhKjbnIqMgCRI/edit?usp=sharing) - Add info on using [GitHub Copilot by OpenAI](https://github.com/features/copilot) or other AI codex.

**Our NAICS pipeline**
We generate local NAICS industry lists and store on GitHub as .csv, .json and .md files:
1. [County Industry files](https://github.com/modelearth/community-data) with 2 to 6 digit NAICS industries hosted on Github.    
2. [Zipcode files with employment levels](https://github.com/modelearth/community-data/tree/master/us/zipcodes/naics) - Includes nunber of Establishments and Employees 
3. [International trade by country](international) - Imports and exports by country by year (to be developed)  

Our implementation of the [US EPA Industry Input-Output Charts](../../../io/charts/) use static files containing [USEEIO API data as json](https://github.com/modelearth/io/tree/main/build/api) for fast page loads.

**[Our Upcoming Industry Input-Output Report](/localsite/info/naics/)** will replace our [Local Industries Impact Report](../../localsite/info/).
<br>

### Community Data File Format

Our NAICS county .csv files have the following columns - [Sample File](https://github.com/modelearth/community-data/blob/master/us/zipcodes/naics/3/0/3/1/8/zipcode30318-census-naics6-2018.csv)<!--[Sample File](https://github.com/modelearth/community-data/blob/master/us/state/GA/naics/GA_data_filled.csv)-->  

**In File Name**
- Zip, FIPS (5-digit state-county ID) or CountryCode (3-characters)  
- NaicsLevel - ActivityProducedBy (6-digit naics)  

**Columns**
- Naics - ActivityProducedBy (6-digit naics)  
- Establishments - Other (Number of Extablishments)  
- Employees - Employment FlowAmount (Number of Employees)  
- Payroll - US Dollars (Annual Wages)
- Population - Included with our Machine Learning output
<br>

Data source: US Bureau of Labor Statistics (BLS)

Older links: [Industries by county](https://github.com/modelearth/community-data/tree/master/us/state) | [Industries by zipcode](../../../community/industries/)  


## Input-Output between Counties

[Commodity Flow Survey (CFS)](https://github.com/modelearth/commodity-flow-survey) - NAICS input-output by county.

## Imputation to fill NAICS Census Gaps

[Removal of Gaps in NAICS Census Business data](research)
Processes that estimate gaps in census employment data.
Eckert Linear Objective Functions and Machine Learning.

<!-- This has been moved:  
To avoid gaps in county industry data, we'll use this [2018 data from Eckert](https://github.com/modelearth/community-data/tree/master/process/cbp).  
-->

<!--
[Embeddable IO Widgets](../../charts) use the [static JSON files](https://github.com/modelearth/io/tree/main/build/api) output from the [USEEIO API](https://github.com/USEPA/USEEIO_API/wiki).
We recommend that you work in [USEEIO-widgets repo](../../charts) if you are interested in interacting with the API data.
-->

<!--
    12-digit FIPS Code - state, county, tract, block group
    https://www.policymap.com/2012/08/tips-on-fips-a-quick-guide-to-geographic-place-codes-part-iii/
-->
<br>


# US EPA Data Source and Integrations

[BEA Global Value Chains](https://www.bea.gov/data/special-topics/global-value-chains)

BLS, EPA's USEEIO and Flowsa (BEA, Energy, Water, more)

## US Census - County Business Patterns (CBP)


## US Bureau of Labor Statistics (BLS)

<!--
Quarterly Census of Employment and Wages (QCEW) - Includes Latitude and Longitude of establishments
-->

## US Census - Quarterly Workforce Indicators (QWI)

Used by [Drawdown Georgia](https://cepl.gatech.edu/projects/Drawdown-Georgia) - [Emissions Dashboard](https://drawdownga.gatech.edu/) for 3-digit NAICS

<a href="https://www.census.gov/data/developers/data-sets/qwi.html">Quarterly Workforce Indicators (QWI)</a>  
[QWI provides 2, 3 and 4 digit NAICS Industries](https://lehd.ces.census.gov/data/schema/latest/lehd_public_use_schema.html#_industry)

<!--
We may combine QWI data with BLS data to estimate 6-digit naics employment and payroll based on the number of firms in a county and additional county attributes.
-->

<!--
* [US Department of Commerce](https://github.com/USEPA/flowsa/wiki/Available-Data#flow-by-activity-datasets)
-->

## US EPA - Flowsa Flow-By-Activity Datasets for USEEIO

[View Ecosystem](../../../io/about/api/) - The US EPA Flowsa data processing library includes:

* [US Bureau of Economic Analysis (BEA)](https://www.bea.gov/data/industries/gross-output-by-industry)
GDP Gross Output, Make Before Redefinitions, Use Before Redefinitions

* [US Bureau of Land Management Public Land Statistics](https://www.blm.gov/about/data/public-land-statistics)

* [Bureau of Labor Statistics Quarterly Census of Employment and Wages](https://www.bls.gov/cew/)  
View our [Flowsa Python scripts](flowsa)

* [Water Withdrawals for the United States](https://pubs.acs.org/doi/abs/10.1021/es903147k?journalCode=esthag)

* [Census Bureau County Business Patterns](https://www.census.gov/programs-surveys/cbp.html)

* [Energy Information Administration - Energy Consumption Survey](https://www.eia.gov/consumption/)
[Manufacturing](https://www.eia.gov/consumption/manufacturing/), [Commercial Buildings](https://www.eia.gov/consumption/commercial/) - Land, Water, Energy - County, Regional and National

* [Inventory of U.S. Greenhouse Gas Emissions and Sinks](https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks)

* [Environmental Protection Agency National Emissions Inventory](https://www.epa.gov/air-emissions-inventories/national-emissions-inventory-nei)

* [More Flowsa data sources...](https://github.com/USEPA/flowsa/wiki/Available-Data#flow-by-activity-datasets) 

<br>


# Display Datasets


#### Embeddable Datasets
<!-- ../#mapview=country -->
[Beyond Carbon State Map](../../../apps/beyondcarbon/#mapview=state) - More embedding samples: [Community Pages](../../../apps)

[Impact Charts](../../../io/charts/) - US Environmentally-Extended Input-Output (USEEIO) - Goods and Services 

[Impact Profiles](../../../io/template/) - Using Environmental Product Declarations (EPDs)


#### Data Sources and Prep

[Community Datasets](https://github.com/modelearth/community-data/) - NAICS Industry Data with Gaps Filled  

[Machine Learning Algorithms for NAICS industries](https://github.com/modelearth/machine-learning/) - US Bureau of Labor Statistics (BLS)

[Impact Heatmap from JSON](/io/build/sector_list.html?view=mosaic&count=50) - [Earlier Goods and Service Heatmap Mockup](../../../community/start/dataset/)


#### Opportunties for further integration

[Google Data Commons Setup](datacommons)  

[DataUSA.io Setup](datausa)  

[Census Reporter](../../../community/resources/censusreporter/)
<!--

[EPA Flowsa Setup](flowsa) - includes U.S. Bureau of Labor Statistics (BLS) industry data  

---
<br>
Are any maps or navigation standards using YAML for layer lists (instead of [json](ga-layers.json)?)  
[YAML Sample](https://nodeca.github.io/js-yaml/) - [Source](https://github.com/nodeca/js-yaml)
-->