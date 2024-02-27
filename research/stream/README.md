[Community Data](/community-data/) 

# Streamlit 


## Random Forests for Honey Bees

[Streamlit Real or Fake (our RealityStream)](https://github.com/ModelEarth/RealityStream) - Logistic Regression, Random Forest and Support Vector Machines.

### Dataset APIs to find
Pull from Google Data Commons using [REST](https://docs.datacommons.org/api/rest/v2/getting_started) and an [Observable Data Loader](https://docs.datacommons.org/api/rest/v2).

These will be used to populate the y=1 value for our [naics training data](../../timelines/training/naics).

- [Bee Pollinator Decline](https://sustainableagriculture.net/blog/pnas-wild-bee-study/)
- Reductions in Tree Canopy
- [Increasing Poverty](https://unstats.un.org/UNSDWebsite/undatacommons/sdgs/goals?v=dc/topic/sdg_1)

## AI Images Generated from Replicate API

We'll be using Streamlit python to generate and save images based on our NAICS industry descriptions and EPA impact indicators.

[generateimages.streamlit.app](https://generateimages.streamlit.app)

[More Streamlit apps](https://streamlit.io/gallery)

## NAICS Data

[NAICS Lookup](https://model.earth/data-pipeline/timelines/tabulator/)

[Annual NAICS data for US counties](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/counties)

## Image Output

We'll generate 10 sample images here in the "[stream/generated](generated)" folder, then automate sending images for all the state-industry-indicator combinations to a new repo called stream-industries.