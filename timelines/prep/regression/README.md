# Regression Prep  

The regression script uses prior years to project forward employment levels. Linear projections seem conservative. Alternative methods could be explored.  

After using steps in ../all/README.md to generate files in output folder.

2.) Run: 

    cd ../regression &&
    python regressor.py  

regressor.py runs tsclean.py.  It generates projected years in data/raw, but doesn't output to a combo file.  


3.) Send files with past and future years to zip folders:

    python mergezip.py ../zipcodes/zcta/zip_to_zcta_2018.csv ../../../community-usa/data/zip/ data/

To try instead:

    python mergezip.py ../ZIPCodetoZCTACrosswalk2022UDS.xlsx ../../../community-usa/data/zip/ data/


combo_zcta_sm.csv   to get data to 2020






DON'T DO THIS

Using tsclean.py

<pre>
# To create projection, change DATA_COMBO_PATH from combo_zcta_sm.csv to combo_zcta_sm_projection.csv
# And change last=2016 to last=2021 in two locations (the furthest in data/raw)
</pre>

OLD:  
tsclean.py creates combo_zcta_sm.csv from files in raw folder, up to last=2016.  

NEW:  
tsclean.py creates combo_zcta_sm.csv from files in input/[year]/[year]\_zcta\_sm.csv, up to last=2016.  

Then use tsclean.py to:

A. Send the projected years to input/[year]/[year]\_zcta\_sm\_projected.csv  
B. Create combo\_zcta\_sm\_projection.csv  


Run:  

<pre>
python mergezip.py ../zipcodes/zcta/zip_to_zcta_2018.csv ../../../community-usa/data/zip/ data/combo_zcta_sm.csv
</pre>

Generates files for each zipcode.  
Save to an external repo due to the size:  
community-usa/data/zip/0/0/0/0/0/[zip]. 

