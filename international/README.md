[Data Pipeline](../)
# International Data Pipeline

[Prepare International Timeline data](../timelines/sqlite/) using [worldbank.org indicators](https://github.com/phiresky/world-development-indicators-sqlite/)

[UN Comtrade Database API](https://comtrade.un.org/data/dev/portal/) - Imports and exports by country by year

[IPCC — Intergovernmental Panel on Climate Change](https://www.ipcc.ch) - The United Nations body for assessing the science related to climate change.

## Data Processing Steps

The UN Comtrade Database API was used to gather data on imports and exports.
For an individual user, the request limit of a single API call is 10,000. 


### Experiments with comtrade/comtrade-script.py

In the comtrade folder, open a commad prompt and run...

Create a virtual environment (OSX / Linux / Windows):
`python3 -m venv .venv`

OSX / Linux:
`source .venv/bin/activate`

Windows:
`\.venv\Scripts\activate.bat`


Not working yet. Generated blank row_ID .csv file previously. 

python3 comtrade-script.py