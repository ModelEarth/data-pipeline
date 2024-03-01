[Community Data](/community-data/) 

# Industries Timeline Data Prep

Run the following in your webroot - so output can be sent to the community-forecasting repo.

	python3 -m venv env &&
	source env/bin/activate &&
	pip install pandas &&
	cd data-pipeline/timelines/prep/industries

Then run:

	python naics-timelines.py


**Output will be saved as:**
community-forecasting/industries/naics/US/AK/US-AK-census-naics4-establishments.csv
community-forecasting/industries/naics/US/AK/US-AK-census-naics4-employees.csv
community-forecasting/industries/naics/US/AK/US-AK-census-naics4-payroll.csv

Sample data on the [tabulator page](../../tabulator/)