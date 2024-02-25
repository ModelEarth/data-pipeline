# UN Comtrade Database API

[UN Comtrade Database API](https://comtrade.un.org/data/dev/portal/) - Imports and exports by country by year


## Data Processing Steps

The UN Comtrade Database API was used to gather data on imports and exports.
For an individual user, the request limit of a single API call is 10,000. 


In the comtrade subfolder, open a commad prompt and run...

Create a virtual environment (OSX / Linux / Windows):
`python3 -m venv .venv`

OSX / Linux:
`source .venv/bin/activate`

Windows:
`\.venv\Scripts\activate.bat`


comtrade-script.py script not working yet. Generated blank row_ID .csv file previously. 

	python3 comtrade-script.py
