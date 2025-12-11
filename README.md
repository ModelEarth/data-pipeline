# Data Pipeline

[Open CEDA](https://watershed.com/solutions/ceda) - 60,000 emission factors, 400 industries, 148 countries
[Exiobase.eu](https://exiobase.io) - International impact factors extending Comtrade UN trade data

The Model.earth data pipeline saves static [Community-Data](/community-data/) and [Community-Timelines](https://github.com/modelearth/community-timelines/) for [state, county](industries/naics/) and [zip code data](/community-zipcodes/) generated for [Industry&nbsp;Supply-Chain IO&nbsp;Charts](https://model.earth/localsite/info/) and [Community Forecasting Timelines](timelines).

Our work with [International Trade Flow SQL](/profile/trade/) and [US State Models data](/io/about/) provides a structure for future models integrated with the [Google Data Commons API](https://docs.datacommons.org/api/) to use [UN Goal Timelines](/data-commons/) in [RealityStream forecasting](/realitystream/).

[View Data Pipeline Nodes from node.csv](../team/projects/#list=data-pipleline)

While USEEIO has been discontinued by the US EPA, their [Embeddable IO Charts](../io/charts/) and [State Impact Reports](../useeio.js/footprint/) provide examples of pulling data from static json files containing [USEEIO state data](https://github.com/ModelEarth/profile/tree/main/impacts/2020) for fast page load times.

<!--
    12-digit FIPS Code - state, county, tract, block group
    https://www.policymap.com/2012/08/tips-on-fips-a-quick-guide-to-geographic-place-codes-part-iii/
-->


#### Embeddable Datasets
<!-- ../#mapview=country -->
[Community Model Pages](../apps) - Parameters for [embedding in local sites](../localsite/)

[Impact Charts](../io/charts/) - US Environmentally-Extended Input-Output (USEEIO) - Goods and Services 

[Impact Profiles](../io/template/) - Using Environmental Product Declarations (EPDs)

#### Product Environmental Data Pipeline

[Products Python Pipeline](https://github.com/ModelEarth/products/tree/main/pull) - Fetches and processes Environmental Product Declarations (EPDs) from BuildingTransparency.org

The products pipeline includes:
- **EPD Data Fetcher** (`product-footprints.py`) - Fetches EPD data for all US states and multiple countries (184,614+ products)
- **Emissions Analyzer** (`analyze_emissions_data.py`) - Analyzes GWP coverage and impact categories across all downloaded EPDs
- **Transportation Impact Calculator** (`calculate_transportation_impact.py`) - Utility functions for calculating A4 stage transportation impacts and adjusting GWP values

**Data Output:** YAML files organized by country and category in [products-data repo](https://github.com/ModelEarth/products-data/)

**Documentation:** [model.earth/products/](https://model.earth/products/) - Full documentation on EPD structure, GWP fields, transportation impacts, and API usage

**Pipeline Nodes:** See `nodes.csv` for `prod_001` (EPD Data Fetcher) and `prod_002` (EPD Emissions Analyzer)


#### Data Sources and Prep

[Community Datasets](https://github.com/modelearth/community-data/) - NAICS Industry Data with Gaps Filled  

[Machine Learning Imputation Algorithms for NAICS industries](https://github.com/modelearth/machine-learning/) - US Bureau of Labor Statistics (BLS)

[Impact Heatmap from JSON](/io/build/sector_list.html?view=mosaic&count=50) - [Earlier Goods and Service Heatmap Mockup](../community/start/dataset/)


#### Pipeline Management

**Unified Pipeline Manager** (`manage_pipelines.py`) - Centralized tool for managing all data update processes

```bash
# List all available pipelines
python manage_pipelines.py list

# Show details for a specific node
python manage_pipelines.py info prod_001

# Run a pipeline node
python manage_pipelines.py run prod_001

# Show dependency chain
python manage_pipelines.py dependencies prod_001

# Show status overview
python manage_pipelines.py status
```

The management script provides:
- **Centralized listing** of all pipeline nodes with metadata
- **Dependency tracking** to understand execution order
- **Unified execution** interface for running any pipeline node
- **Status overview** with statistics on processing times and capabilities

All pipeline nodes are documented in `nodes.csv` and `nodes.json` for integration with workflow automation tools like n8n.

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