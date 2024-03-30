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

TO DO:

Remove .0
Loop through array of 2-char state abbreviations. Rerun to increase from 42 to 50.
Incude all of USA USEEIOv2.0.1-411 (save in same folder with states)

TO DO: Find international commodity and/or economic data in [Google Data Commons](https://docs.datacommons.org/api/) or [UN Comtade Data](/data-pipeline/international/)

TO DO: Wes - Add notes here on which commodities are excluded (small business, gov, etc.)

