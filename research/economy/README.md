[Active Projects](../../../projects/)

# Top Commodities by State

[Our Input-Output Model](/io/about/matrix/) includes [commodity vector q](https://smmtool.app.cloud.gov/api/USEEIOv2.0.1-411/matrix/q) from the [EPA Widget API](/io/charts/).
We calculate the upstream direct requirements, direct impacts, and direct downstream monetary flows related to this vector.

To run [JobsD+q-2csv.py](https://github.com/ModelEarth/data-pipeline/tree/main/research/economy)

	python3 -m venv env
	source env/bin/activate
	pip install numpy
	pip install pandas
	pip install requests
	python JobsD+q-2csv.py



We omitted Rest of US (RoUS) rows.
But let's document why RoUS values differ from US output.

TO DO: Add notes regarding which commodities are excluded (small business, gov, etc.)

TO DO: Find international commodity data in [Google Data Commons](https://docs.datacommons.org/api/) and display [EXIOBASE charts](https://exiobase.eu).

Learn about [Input-Output Model Construction](/io/about/matrix/). &nbsp;View [Javascript Open Footprint](/useeio.js/footprint/).