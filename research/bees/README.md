[Training Data ML](../../timelines/training/naics/)
# Bee the Predictor (y=1 training data)

## Datasets

Pull from Google Data Commons using [REST](https://docs.datacommons.org/api/rest/v2/getting_started) and store with a [Observable Data Loader](https://docs.datacommons.org/api/rest/v2).

These will be used to populate the y=1 value for our [naics training data](../../timelines/training/naics).

### Bee Pollinators

- Bee Pollinators USDA
- [Bee Pollinator Decline](https://sustainableagriculture.net/blog/pnas-wild-bee-study/) - Is there an accessible (free) source?


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