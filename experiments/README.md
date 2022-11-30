# GitHub Action Workflows

Workflow actions not yet set up here in the data-pipeline repo.



## Build from source

Create a virtual environment (OSX / Linux / Windows):
`python3 -m venv .venv`

OSX / Linux:
`source .venv/bin/activate`

Windows:
`\.venv\Scripts\activate.bat`

Running `make dependencies` will install BeautifulSoup4

1. `make dependencies`
2. `make test`
3. `python3 -m app scrape > scraped/atl-citycouncil.json`

Change line 3 above.  
Use this sample of including a Python script in GitHub Actions:  

https://github.com/abrie/atl-council-scraper

We'll run our [Python comtrade script](https://github.com/modelearth/data-pipeline/tree/main/international/comtrade) to populate folders for each country.  
