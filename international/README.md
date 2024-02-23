[Data Pipeline](../)
# International Data API

[Google Data Commons API for UN Global Goals](https://blog.google/technology/ai/google-ai-data-un-global-goals/) - [UN Data Commons: SDG Data by Goal](https://unstats.un.org/UNSDWebsite/undatacommons/sdgs)
The UN Sustainable Development Goals (SDG) data resides in the [Google Data Commons API](https://docs.datacommons.org/api/).

[Update our Google Data Commons notes page](../../localsite/info/data/datacommons/) - Add steps for using the API and generate visualizations

[Prep Timeline Data](../timelines/) using [worldbank.org indicators](https://github.com/phiresky/world-development-indicators-sqlite/)



[UN Comtrade Database API](https://comtrade.un.org/data/dev/portal/) - Imports and exports by country by year

[Intergovernmental Panel on Climate Change (IPCC)](https://www.ipcc.ch) - The UN body for assessing the science related to climate change.

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