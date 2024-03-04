[Community Data](/community-data/) 

# Industries Timeline Data Prep

Run the following in your webroot - so output can be sent to the community-forecasting repo.

	python3 -m venv env &&
	source env/bin/activate &&
	pip install pandas &&
	cd data-pipeline/timelines/prep/industries

Then run:

	python naics-timelines.py


**Output is saved to:**
[community-timelines/industries/naics4/US/states/](https://github.com/ModelEarth/community-timelines/tree/main/industries/naics4/US/states)
community-timelines/industries/naics4/US/states/AK/US-AK-census-naics4-establishments.csv
community-timelines/industries/naics4/US/states/AK/US-AK-census-naics4-employees.csv
community-timelines/industries/naics4/US/states/AK/US-AK-census-naics4-payroll.csv

Sample data on the [tabulator page](../../tabulator/)