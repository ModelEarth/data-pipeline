[Community Data](/community-data/) 

# Streamlit 

## Random Forests for Honey Bees

[Kishor's Image Repo](https://github.com/mannurkishorreddy/streamlit-replicate-img-app) - [Our Fork](https://github.com/ModelEarth/replicate)

[Our RealityStream](https://github.com/ModelEarth/RealityStream) - Logistic Regression, Random Forest and Support Vector Machines <!-- probably-->from [Streamlit App Gallery](https://streamlit.io/gallery)

The Prompt CSV files contain Top 4 Industries in Maine and Oregon, with 4 images of each

Create a Python script at research/stream/industries-prompt.py to  
generate a CSV file with the top 4 Establishment rows from our 
[Maine 2021 Industry list](https://model.earth/community-data/industries/naics/US/counties/ME/US-ME-census-naics4-2021.csv) and [Oregon 2021 Industry list](https://model.earth/community-data/industries/naics/US/counties/OR/US-OR-census-naics4-2021.csv).

Use parameters for: country (US), stateAbbr (ME and OR), naicsLevel (4), year (2021), state (Maine and Oregon), outputFolder (prompts/industries)

Join with the Industry titles from our [NAICS Lookup CSV](https://model.earth/community-data/us/id_lists/industry_id_list.csv).

Save the column names as:

Naics
Industry
Prompt
Establishments
Employees
Payroll

Populate the Prompt column with these four for each (16 total):
- A honey bee is near a location that provides [Industry] in Maine in 2021.
- A street under a tree canopy near a location that provides [Industry] in Maine in 2021.
- An innovation that creates jobs in [Industry] in Maine in 2021.
- An innovation that reduces poverty in [Industry] in Maine in 2021.

Send the output to 2 files in a prompts/industries subfolder:

prompts/industries/ME-prompts-2021.csv
prompts/industries/OR-prompts-2021.csv

The y=1 value will be set by [Census Data](https://www.censusreporter.org/data/map/?table=B06011&geo_ids=040|01000US) and [Bee Pollinator](../bees/) data


## AI Images Generated from Replicate API

We'll be using Streamlit python to generate and save images based on our NAICS industry descriptions and EPA impact indicators.

[generateimages.streamlit.app](https://generateimages.streamlit.app)

[More Streamlit apps](https://streamlit.io/gallery)

## NAICS Data

[NAICS Lookup](https://model.earth/data-pipeline/timelines/tabulator/)

[Annual NAICS data for US counties](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/counties)

## Image Output

We'll generate 10 sample images here in the "[stream/generated](generated)" folder, then automate sending images for all the state-industry-indicator combinations to a new repo called stream-industries.