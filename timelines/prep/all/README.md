[Community Data](../../../../community-data/)

# NAICS Timeline Data for ML

Our recent work resides at [timelines/training/naics](../../training/naics)

## NAICS Timelines - Generate Multiple Years

<!--Each year, at the end of April (or later... was Nov in 2019), get the latest industry file. -->

The old data source was annual files containing locations (zip) and 11 industry columns.
[input/2017/2017_zcta_industries_sm.csv](input/2017/2017_zcta_industries_sm.csv)

zcta, latitude, longitude,JobsTotal,JobsAgriculture,JobsAutomotive,JobsEntertainment,JobsConstruction,JobsHealthcare,JobsManufacturing,JobsProfessional,JobsRealestate,JobsTrade,JobsTransport
30318,33.79,-84.45,1626,,2,132,78,92,83,303,87,164,41
30319,33.88,-84.33,974,1,,70,43,70,11,317,120,56,3
30322,33.79,-84.33,54,,,,,11,,1,,1,
30324,33.82,-84.36,1008,1,,63,38,100,22,234,77,46,12
...

Our new data is annual files with locations (county fips) and rows for each ciounty's industries - with 3 indicators.

Fips, Naics, Establishments, Employees, Payroll
02016,7225,5,42,1113
02016,8139,4,22,1506
02016,1141,5,6,602
02016,3117,5,2514,70547
...

### Always start a virtual environment first

Run in your webroot since you'll be sending output to the community-forecasting repos.

	python3 -m venv env && source env/bin/activate &&
	cd data-pipeline/timelines/prep/all

To run new cmds in the same virtual environment, in a new prompt run:

	source env/bin/activate
	
### Output SQLite script for years
Create a sqlite generator for each year: zcta\_2017.SQL.txt  
These import data from [input/2017/2017_zcta_industries_sm.csv](input/2017/2017_zcta_industries_sm.csv)

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

Run in your virtual env:
	
	pip install pandas &&
	pip install scikit-learn

1.) Change to the "python" subfolder, run Random Forest (uses python/runOneFile.py):
Takes about a minute.

	cd python &&
	python automateRF.py "../output"


The 2016/2016_random_forest_poverty.csv file is not generated due to this error:

Error from: python automateRF.py "../output"
~~~
OutFile Generated: /Users/helix/Library/Data/data-pipeline/timelines/prep/all/output/2013/2013_random_forest_poverty.csv  
OutFile Generated: /Users/helix/Library/Data/data-pipeline/timelines/prep/all/output/2014/2014_random_forest_poverty.csv  
OutFile Generated: /Users/helix/Library/Data/data-pipeline/timelines/prep/all/output/2015/2015_random_forest_poverty.csv  
Traceback (most recent call last):  
File "automateRF.py", line 35, in module
main()  
File "automateRF.py", line 30, in main  
for file in os.listdir(os.path.join(inDir,subDir)):  
NotADirectoryError: [Errno 20] Not a directory: '../output/.DS_Store'
~~~

2.) Create a summary file. Run in timelines/summary folder:

	cd ../summary/ &&
	sqlite3 summary.db < summary.SQL.txt > summary.OUT.txt

<!--
3.) We can probably skip this.  It didn't update files.  Removed zip folder.

Generate zips folders (zip crosswalk will need to be updated every 2 to 5 years)
This step takes over 12 minutes to run.

	cd ../ &&
	pip install openpyxl &&
	python zipgraph.py ZIPCodetoZCTACrosswalk2022UDS.xlsx ../../zip/
	
Sample output for 0/0/5/0/1:

# Holtsville, NY, 00501 
ZCTA 11742.0 
-->
<!-- Post Office or large volume customer -->


3.) See readme in [regression](../regression)

Runs mergezip.py and mergezip.py
Previously sent zip files with projections to: [/community-usa/data/zip/](https://github.com/ModelEarth/community-usa/tree/main/data/zip)

New process will send to: [/community-timelines/industries/zcta/predictions/](https://github.com/ModelEarth/community-timelines/)

Previous output:
Columns: Year	JobsTotal	JobsAgriculture	jobsEntertainment	JobsConstruction	 JobsHealthcare	 JobsManufacturing	 JobsProfessional	 JobsRealestate	 JobsTrade	 JobsTransport	 Population	 Poverty	 Poverty_Under18	 Poverty_18to65	 Poverty_Over65	 Education	 Work_Experience	 Working_Fulltime	 Working_Fulltime_Poverty 

Rows: 2012 to 2021

TO DO: [NAICS zip processing](/data-pipeline/industries/naics/) - Using same API as counties

