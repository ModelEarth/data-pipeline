[Community Data](/community-data/)
# Data Pipeline

[Our Community Datasets](/community-data/) and [Community Timelines Repo](https://github.com/modelearth/community-timelines/) contain state, county and zip code data generated for regional [ML&nbsp;Timelines for Forecasting](timelines) and [Industry&nbsp;Supply-Chain IO&nbsp;Charts](https://model.earth/localsite/info/)<!--[Map&nbsp;Topics](#appview=topics&geoview=country)-->.

View our [Active Projects](/projects/) and our [Observable Framework Dev](/data-commons/dist/) for the [Google Data Commons API](https://docs.datacommons.org/api/).

Our implementation of the [US EPA Industry Input-Output Charts](../io/charts/) uses static json files containing [USEEIO API data](https://github.com/modelearth/io/tree/main/build/api) for fast loading pages.

We are working toward adding a [Requests Agent](/requests/) to [Open WebUI](/projects/src) and [Earthscape](/earthscape/app).

[Learn about the three APIs](/io/coders) we are combining for requests: [FDA](/data-commons/docs/food/), See Click Fix, Open Collective

<!--
    12-digit FIPS Code - state, county, tract, block group
    https://www.policymap.com/2012/08/tips-on-fips-a-quick-guide-to-geographic-place-codes-part-iii/
-->
<br>

# Data Source and Integrations

## US Census - County Business Patterns (CBP)

[We process annual US naics industry levels](timelines/)
CSV files are saved for counties and states. Zip and country-wide files coming soon.
Results are used to [compare local industries](../localsite/info)

## US Bureau of Labor Statistics (BLS)

We integrate with US EPA's USEEIO and Flowsa (BEA, Energy, Water, more)
[BEA Global Value Chains](https://www.bea.gov/data/special-topics/global-value-chains)


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

[View Ecosystem](../../io/about/api/) and [Lifecycle Tools Overview](../../community/tools/) - The US EPA Flowsa data pipeline includes:

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
[Community Model Pages](../apps) - Parameters for [embedding in local sites](../localsite/)

[Impact Charts](../io/charts/) - US Environmentally-Extended Input-Output (USEEIO) - Goods and Services 

[Impact Profiles](../io/template/) - Using Environmental Product Declarations (EPDs)


#### Data Sources and Prep

[Community Datasets](https://github.com/modelearth/community-data/) - NAICS Industry Data with Gaps Filled  

[Machine Learning Imputation Algorithms for NAICS industries](https://github.com/modelearth/machine-learning/) - US Bureau of Labor Statistics (BLS)

[Impact Heatmap from JSON](/io/build/sector_list.html?view=mosaic&count=50) - [Earlier Goods and Service Heatmap Mockup](../community/start/dataset/)


#### Opportunties for further integration

[Google Data Commons Setup](../localsite/info/data/datacommons)  

[DataUSA.io Setup](../localsite/info/data/datausa/)  

[Census Reporter](../community/resources/censusreporter/)
<!--

[EPA Flowsa Setup](flowsa) - includes U.S. Bureau of Labor Statistics (BLS) industry data  

---
<br>
Are any maps or navigation standards using YAML for layer lists (instead of [json](ga-layers.json)?)  
[YAML Sample](https://nodeca.github.io/js-yaml/) - [Source](https://github.com/nodeca/js-yaml)

[LA's Public Tree Map](https://neighborhood.org/public-tree-map/) - [Pipeline](https://github.com/Public-Tree-Map/public-tree-map-data-pipeline) contains 30,000+ records.
-->