### This file contains the configuration used to make API requests to copernicus

from pathlib import Path

class DataConfig:
    DATA_PATH = Path("data")

    HISTORICAL_PERIOD = [
        "2000",
        "2001",
        "2002",
        "2003",
        "2004",
        "2005",
        "2006",
        "2007",
        "2008",
        "2009",
        "2010",
        "2011",
        "2012",
        "2013",
        "2014",
    ]

    PROJECTIONS_PERIOD = [
        "2019",
        "2020",
        "2021",
        "2022",
        "2023",
        "2024",
        "2025",
        "2026",
        "2027",
        "2028",
        "2029",
        "2030",
    ]

    EXTREME_PRECIPITATION_DATASET = "sis-european-risk-extreme-precipitation-indicators"

    EXTREME_PRECIPITATION_VARIABLES = {
        "maximum_1_day_precipitation": "max-1day-precipitation",
        "maximum_5_day_precipitation": "max-5day-precipitation",
        "number_of_consecutive_wet_days": "number-of-consecutive-wet-days",
        "number_of_precipitation_days_exceeding_20mm": "number-of-events-exceeding-20mm",
        # "number_of_precipitation_days_exceeding_fixed_percentile": "number-of-events-exceeding-fixed-percentile",
        "number_of_wet_days": "number-of-wet-days",
        "total_precipitation": "total-precipitation",
    }

    EXTREME_PRECIPITATION_REQUEST = {
        "spatial_coverage": ["europe"],
        "variable": list(EXTREME_PRECIPITATION_VARIABLES.keys()),
        "product_type": ["e_obs"],
        "temporal_aggregation": [
            "monthly",
        ],
        "percentile": [
            "99th"
        ],
        "period": HISTORICAL_PERIOD
    }

    PROJECTIONS_DATASET = "projections-cmip6"

    PROJECTIONS_EXPERIMENTS = ["historical", "ssp1_2_6", "ssp2_4_5", "ssp5_8_5"]

    PROJECTIONS_VARIABLES = ["precipitation", "air_temperature"]

    PROJECTIONS_MODELS = ["cnrm_cm6_1"]

class ProjectionRequest:
    def __init__(self, model, variable, experiment, period):
        self.model = model
        self.variable = variable
        self.experiment = experiment
        self.period = period

    def get_request(self):
        return {
            "temporal_resolution": "monthly",
            "experiment": self.experiment,
            "variable": self.variable,
            "model": self.model,
            "year": self.period,
            "month": [
                "01", "02", "03",
                "04", "05", "06",
                "07", "08", "09",
                "10", "11", "12"
            ],
            "area": [71, -25, 35, 45] # Europe
        }