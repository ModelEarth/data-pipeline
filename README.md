[Community Data](/community-data/)
# Data Pipeline

[Our Community Data Repo](/community-data/) contains state, county and zip code data generated for regional [Industry&nbsp;IO&nbsp;Charts](https://model.earth/localsite/info/), [Map&nbsp;Topics](#appview=topics&geoview=country) and [timelines](timelines).

Our implementation of the [US EPA Industry Input-Output Charts](../../../io/charts/) uses static json files containing [USEEIO API data](https://github.com/modelearth/io/tree/main/build/api) for fast page loads.


<!--
    12-digit FIPS Code - state, county, tract, block group
    https://www.policymap.com/2012/08/tips-on-fips-a-quick-guide-to-geographic-place-codes-part-iii/
-->


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

[Machine Learning Imputation Algorithms for NAICS industries](https://github.com/modelearth/machine-learning/) - US Bureau of Labor Statistics (BLS)

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

[LA's Public Tree Map](https://neighborhood.org/public-tree-map/) - [Pipeline](https://github.com/Public-Tree-Map/public-tree-map-data-pipeline) contains 30,000+ records.
-->