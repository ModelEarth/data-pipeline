# UN Comtrade Database API

Comtrade data is the backbone of Exiobase.
Our active work occurs in the [Exiobase/tradeflow](/exiobase/tradeflow) folder.

## Comtrade API

[UN Comtrade Database API](https://comtrade.un.org/data/dev/portal/) - Imports and exports by country by year

The UN Comtrade Database API provides imports and exports WITHOUT impacts.
For an individual user, the request limit of a single API call is 10,000. 


In the comtrade subfolder, open a commad prompt and run...

Create a virtual environment (OSX / Linux / Windows):
`python3 -m venv .venv`

OSX / Linux:
`source .venv/bin/activate`

Windows:
`\.venv\Scripts\activate.bat`

To run new cmds in the same virtual environment, in a new prompt run:

	source env/bin/activate

comtrade-script.py script not working yet. Generated blank row_ID .csv file previously. 

	python3 comtrade-script.py
