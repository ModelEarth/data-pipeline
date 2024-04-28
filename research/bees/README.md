[Training Data ML](../../timelines/)
# Bee the Predictor (y=1 training data)

## Datasets

[Our RealityStream Repo](https://github.com/ModelEarth/RealityStream) contains three ML Classification Models: Logistic Regression, Random Forest and Support Vector Machines.

To run locally, place a copy of our [CoLab](https://colab.research.google.com/drive/1o7HXhOl_NWhVm4Nn6L-sjDHsn0bokgeI?usp=sharing) in our [Location Forest](/RealityStream/models/location-forest/).

We're also pulling y=1 data from the Google Data Commons API using [REST](https://docs.datacommons.org/api/rest/v2/getting_started) via [Observable Data Loaders](https://observablehq.com/framework/loaders).

We'll be using both python and javascript to merge y=1 values for counties into our [naics training data](../../timelines/training/naics). Trainging datasets for countries, states/territories and postal codes (zip/zcta) are also being created. 

### Bee Pollinators

- Bee Pollinators USDA
<!-- - [Bee Pollinator Decline](https://sustainableagriculture.net/blog/pnas-wild-bee-study/) -->


### Additional y=1

- Reductions in Tree Canopy
- [Increasing Poverty](https://unstats.un.org/UNSDWebsite/undatacommons/sdgs/goals?v=dc/topic/sdg_1)


<div style="overflow:auto; margin-top:0px; padding-right:50px">

  <div style="font-size:16px">
  <b><span class="yeartext"></span>[Prior change] predicting [future] change at locations or in industry mix</b><br>
  For model training, a "y" column value of 1 indicate locations where [Attribute(s)] that changed in a [prior year] predict a later year.<br><br>
  </div>

  <div style="background:#fff; padding:20px; max-width:600px">
	  <img src="https://model.earth/community-forecasting/about/img/random-forest.webp" style="width:100%;"><br>
	</div>

  <div style="display:none;font-size:12pt;line-height:16pt;padding-top:20px">
    Best Params: 
    max depth: 8; <!-- max number of levels in each decision tree -->
    n-estimators: 100 <!-- number of trees in the foreset --><br>

    Accuracy before tuning: 69%.&nbsp;
    Accuracy after tuning: 71%.
  </div>
  
</div>