# GitHub Action Workflows

Use this sample of including a Python script in GitHub Actions:  

Run on our [Python comtrade script](../international/comtrade) to populate folders for each country. 


## Build from source

Create a virtual environment (OSX / Linux / Windows):
`python3 -m venv env`

OSX / Linux:
`source env/bin/activate`

Windows:
`\env\Scripts\activate.bat`

To run new cmds in the same virtual environment, in a new prompt run:

	source env/bin/activate

Running `make dependencies` will install BeautifulSoup4

1. `make dependencies`
2. `make test`
3. `python3 -m app scrape > scraped/somedata.json`

# Change line 3 above.  Source: https://github.com/abrie/atl-council-scraper
 
