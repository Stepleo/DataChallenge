# Template Kit for RAMP challenge

[![Build status](https://github.com/ramp-kits/template-kit/actions/workflows/test.yml/badge.svg)](https://github.com/ramp-kits/template-kit/actions/workflows/test.yml)

## Introduction

### Main Goal:

#### CEMS GLOFAS Historical Dataset

##### Overview
The CEMS GLOFAS Historical dataset provides gridded daily hydrological time series, including key variables such as river discharge, soil wetness index, snow depth, and runoff water equivalent. This dataset is produced by the Global Flood Awareness System (GloFAS).

##### Key Features
- **Main Variables**:
  - River discharge in the last 24 hours (Main flood target variable)
  - Runoff water equivalent
  - Snow depth water equivalent
  - Soil wetness index


#### CMIP6 Global Climate Projections Dataset

##### Overview
The CMIP6 dataset provides daily and monthly global climate projections from various experiments and models. It supports the Intergovernmental Panel on Climate Change (IPCC) 6th Assessment Report, aiding in understanding climate change, predictability, and model realism.

##### Key Features
- **Climate Scenarios**: This dataset contains climate predictions according to how our CO2 emissions grow. They showcase different experiments with different codenames: "ssp1_2_6" for Low emissions, "ssp2_4_5" for Medium emissions and"ssp5_8_5" for High emissions
- **Main Variables**:
  - Air temperature
  - Precipitation
  - Snow depth
  - Total runoff
  - Moisture in upper portion of soil column
  These variables are "similar" to the ones in the previous dataset.

Our main idea was to 
- try and  train a model to predict the level of flooding from the other 3 variables in the GLOFAS dataset. 
- We would then use CMIP's projected meteorological data to predict flood level according to the different emissions scenarios.


#### Setbacks

Unfortunatelt the API use was not ergonomic. The requests use .nc compressed files that can only download one variable at a time. Although both datasets come from copernicus they require changing the API key config. We had trouble decompressing the .nc files

## Getting started

### Install

To run a submission and the notebook you will need the dependencies listed
in `requirements.txt`. You can install install the dependencies with the
following command-line:

```bash
pip install -U -r requirements.txt
```




<!-- 
### Challenge description

Get started on this RAMP with the
[dedicated notebook](template_starting_kit.ipynb). -->

<!-- ### Test a submission

The submissions need to be located in the `submissions` folder. For instance
for `my_submission`, it should be located in `submissions/my_submission`.

To run a specific submission, you can use the `ramp-test` command line:

```bash
ramp-test --submission my_submission
```

You can get more information regarding this command line:

```bash
ramp-test --help
```

### To go further

You can find more information regarding `ramp-workflow` in the
[dedicated documentation](https://paris-saclay-cds.github.io/ramp-docs/ramp-workflow/stable/using_kits.html) -->
