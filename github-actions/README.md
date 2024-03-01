# GitHub Action Workflows

Use this sample of including a Python script in GitHub Actions:  

Run on our [Python comtrade script](../international/comtrade) to populate folders for each country. 


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
3. `python3 -m app scrape > scraped/somedata.json`

# Change line 3 above.  Source: https://github.com/abrie/atl-council-scraper
 
