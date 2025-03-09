# DataCamp

## Introduction

### Main Goal:

#### CEMS GLOFAS Historical Dataset

##### Overview
The CEMS GLOFAS Historical dataset provides gridded daily hydrological time series, including key variables such as `river discharge`, `soil wetness index`, `snow depth`, and `runoff water equivalent`. This dataset is produced by the Global Flood Awareness System (GloFAS). [Link](https://ewds.climate.copernicus.eu/datasets/cems-glofas-historical?tab=overview)

##### Key Features
- **Main Variables**:
  - `river discharge` in the last 24 hours (Main flood target variable)
  - `runoff water equivalent`
  - `snow depth water equivalent`
  - `soil wetness index`

#### CMIP6 Global Climate Projections Dataset

##### Overview
The CMIP6 dataset provides daily and monthly global climate projections from various experiments and models. It supports the Intergovernmental Panel on Climate Change (IPCC) 6th Assessment Report, aiding in understanding climate change, predictability, and model realism. [Link](https://cds.climate.copernicus.eu/datasets/projections-cmip6?tab=overview)

##### Key Features
- **Climate Scenarios**: This dataset contains climate predictions according to how our CO2 emissions grow. They showcase different experiments with different codenames: `ssp1_2_6` for Low emissions, `ssp2_4_5` for Medium emissions, and `ssp5_8_5` for High emissions.
- **Main Variables**:
  - `air temperature`
  - `precipitation`
  - `snow depth`
  - `total runoff`
  - `moisture in upper portion of soil column`
  These variables are "similar" to the ones in the previous dataset.

Our main idea was to:
- Train a model to predict the level of flooding from the other 3 variables in the GLOFAS dataset.
- Use CMIP's projected meteorological data to predict flood levels according to the different emissions scenarios.

#### Setbacks

Unfortunately, the API use was not ergonomic. The requests use `.nc` compressed files that can only download one variable at a time. Although both datasets come from Copernicus, they require changing the API key config. We managed to decompress the files into `flood_risk_data.csv` and `ssp_{id}.csv`, but transforming the target into a categorical variable did not work well as the variables were not an exact match (`snow_depth` != `snow_flux`), and it's unclear for water runoff. This meant our accuracy was not great, and our hypothesis of higher emission hypothesis = higher flood risk was not validated.

Which means we had to create a ground truth some other way for our study. We used a Precipitation dataset [Link](https://cds.climate.copernicus.eu/datasets/sis-european-risk-extreme-precipitation-indicators?tab=download) to create a placeholder that we'll try to predict. This is what `X_train` and `X_test` contain: historical data from the CMIP dataset with a placeholder variable created from the Precipitation dataset. We try to predict the placeholder target using the two variables `air_temp` and `precipitation`. This is what the main `ramp-workflow` module is set up with, and what `ramp-test` will run. Check the next part for more information.

## Getting Started

### Install

To run a submission and the notebook, you will need the dependencies listed in `requirements.txt`. You can install the dependencies with the following command-line:

```bash
pip install -U -r requirements.txt
```

For testing the impact of emissions, we propose these two files as we could not find a way to save a model trained by ramp-workflow or use it for inference. experiment 1 uses the placeholder value in X_train and X_test.
``` bash
python experiment1.py
``` 

Experiment 2 uses the real discharge value from the GLOFAS dataset to check that theory.

``` bash
python experiment2.py
``` 

The expected outcomes of these files was to check that in the different scenrios we predict different levels of risk. High emissions mean worse climate predictions and more flood risk. Unfortunately we were not able to prove that.

### API

If you wish to setup the API you need to create an account in the previously linked website to get a key.

That key **needs** to be stored in `~/.cdsapirc` or `Users/$User/.cdsapirc`. You can follow their instructions on how to setup the API on their website and then use `download_data.py` but this will require changing the url in the hidden key file after downloading precipitations as we will be downloading from two diffrent URls. This is not recommended. stick with the pushed CSVs for a better experience