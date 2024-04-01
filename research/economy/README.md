[Active Projects](../../../io/)

# Deep Learning Economy

[Our Input-Output Model](/io/about/matrix/) includes [commodity vector q](https://smmtool.app.cloud.gov/api/USEEIOv2.0.1-411/matrix/q) from the [EPA Widget API](/io/charts/).
We calculate the upstream direct requirements, direct impacts, and direct downstream monetary flows related to this vector.

To run JobsD+q-2csv.py

	python3 -m venv env &&
	source env/bin/activate &&
	pip install numpy &&
	pip install pandas &&
	pip install requests &&
	python JobsD+q-2csv.py


TO DO: We'll omit Rest of US (RoUS) rows, but first let's document why RoUS values differ from US output.

TO DO: Find international commodity data in [Google Data Commons](https://docs.datacommons.org/api/).

TO DO: Add notes regarding which commodities are excluded (small business, gov, etc.)

