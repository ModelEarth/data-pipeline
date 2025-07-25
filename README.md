# Data Pipeline

[Open CEDA](https://watershed.com/solutions/ceda) - 60,000 emission factors, 400 industries, 148 countries
[Exiobase.eu](https://exiobase.io) - International impact factors extending Comtrade UN trade data

The Model.earth data pipeline saves static [Community-Data](/community-data/) and [Community-Timelines](https://github.com/modelearth/community-timelines/) for [state, county](industries/naics/) and [zip code data](/community-zipcodes/) generated for [Industry&nbsp;Supply-Chain IO&nbsp;Charts](https://model.earth/localsite/info/) and [Community Forecasting Timelines](timelines).

[Our Embeddable IO Charts](../io/charts/) and [State Impact Reports](../useeio.js/footprint/) pull from static json files containing [USEEIO state data](https://github.com/ModelEarth/profile/tree/main/impacts/2020).

Our work with [International Trade Flow SQL](/profile/trade/) and [US State Models data](/io/about/) provides a structure for future models integrated with the [Google Data Commons API](https://docs.datacommons.org/api/) to use [UN Goal Timelines](/data-commons/) in [RealityStream forecasting](/realitystream/).

[View Data Pipeline Nodes from node.csv](../team/projects/#list=data-pipleline)

<!--
    12-digit FIPS Code - state, county, tract, block group
    https://www.policymap.com/2012/08/tips-on-fips-a-quick-guide-to-geographic-place-codes-part-iii/
-->


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