### Data Sources

## County Business Patterns (CBP)

[Annual US Census naics industry levels](timelines/)
CSV files are saved for counties and states.  
Zip and country-wide files coming soon.  
Results are used to [compare local industries](../localsite/info)

## US Bureau of Labor Statistics (BLS)

US EPA's USEEIO and Flowsa
(BEA, Energy, Water, more)
[BEA Global Value Chains](https://www.bea.gov/data/special-topics/global-value-chains)


<!--
Quarterly Census of Employment and Wages (QCEW) - Includes Latitude and Longitude of establishments
-->

## Quarterly Workforce Indicators (QWI)

US Census data used by [Drawdown Georgia](https://cepl.gatech.edu/projects/Drawdown-Georgia)
[Emissions Dashboard](https://drawdownga.gatech.edu/) for 3-digit NAICS

<a href="https://www.census.gov/data/developers/data-sets/qwi.html">Quarterly Workforce Indicators (QWI)</a>  
[QWI provides 2, 3 and 4 digit NAICS Industries](https://lehd.ces.census.gov/data/schema/latest/lehd_public_use_schema.html#_industry)

<!--
We may combine QWI data with BLS data to estimate 6-digit naics employment and payroll based on the number of firms in a county and additional county attributes.
-->

<!--
* [US Department of Commerce](https://github.com/USEPA/flowsa/wiki/Available-Data#flow-by-activity-datasets)
-->

## US EPA - Flow-By-Activity (Flowsa)
USEEIO Datasets

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