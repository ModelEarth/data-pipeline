[Community Data](../../../../community-data/)

# NAICS Timeline Data for ML

## NAICS Timelines - Generate Multiple Years

Each year, at the end of April (or later... was Nov in 2019), get the latest industry file.   

### Output SQLite script for years
Create a sqlite generator for each year: zcta\_2017.SQL.txt  
Imports data from [input/2017/2017_zcta_industries_sm.csv](input/2017/2017_zcta_industries_sm.csv)

	python automate.py zcta.SQL.txt

### Send annual training files to output folder
output/[year]/[year]\_zcta_sm.csv

zcta, JobsTotal, JobsAgriculture, JobsEntertainment,...
Population, Poverty, Poverty_Under18, Education,Work_Experience, Working_Fulltime, Working_Fulltime_Poverty, y

Where last column y is 1 or 0.


	./run.sh

Or run years individually:

	sqlite3 zcta.db < zcta_2013.SQL.txt> zcta.OUT.txt  

This sends files to data/[year]

----

# Random Forest and Regression

Make new edits to zcta.SQL.txt, then update line numbers in automate.py.

Annual zcta_[year].SQL.txt files are overwritten by automate.py.  

Might need:
	
	python3 -m venv env &&
	source env/bin/activate &&
	pip install pandas &&
	pip install scikit-learn

1.) Run Random Forest (uses python/runOneFile.py):

	cd python
	python automateRF.py "../output"

2.) Create a summary file. Run in timelines/summary folder:

	cd ../../summary/
	sqlite3 summary.db < summary.SQL.txt > summary.OUT.txt

3.) Generate zips folders using instructions in zipgraph.py

	pip install openpyxl
	python zipgraph.py ZIPCodetoZCTACrosswalk2022UDS.xlsx ../../zip/
	
4.) See readme in [regression](../regression)

5.) Also see [Processing NAICS by Zip Code](/community-data/process/naics/) 