from pathlib import Path

class DataConfig:
    DATA_PATH = Path("data")

    # Time periods
    HISTORICAL_PERIOD = [str(year) for year in range(2000, 2015)]
    PROJECTIONS_PERIOD = [str(year) for year in range(2019, 2031)]
    FLOOD_DATA_PERIOD = [str(year) for year in range(2000, 2025)]

    # Precipitation Data
    EXTREME_PRECIPITATION_DATASET = "sis-european-risk-extreme-precipitation-indicators"

    EXTREME_PRECIPITATION_VARIABLES = {
        "maximum_1_day_precipitation": "max-1day-precipitation",
        "maximum_5_day_precipitation": "max-5day-precipitation",
        "number_of_consecutive_wet_days": "number-of-consecutive-wet-days",
        "number_of_precipitation_days_exceeding_20mm": "number-of-events-exceeding-20mm",
        "number_of_wet_days": "number-of-wet-days",
        "total_precipitation": "total-precipitation",
    }

    EXTREME_PRECIPITATION_REQUEST = {
        "spatial_coverage": ["europe"],
        "variable": list(EXTREME_PRECIPITATION_VARIABLES.keys()),
        "product_type": ["e_obs"],
        "temporal_aggregation": ["monthly"],
        "percentile": ["99th"],
        "period": HISTORICAL_PERIOD,
    }

    # CMIP6 Projections Data
    PROJECTIONS_DATASET = "projections-cmip6"
    PROJECTIONS_EXPERIMENTS = ["historical", "ssp1_2_6", "ssp2_4_5", "ssp5_8_5"]
    PROJECTIONS_VARIABLES = ["precipitation", "air_temperature","total_runoff","snowfall_flux"]
    PROJECTIONS_MODELS = ["cnrm_cm6_1"]

    # Flood Risk Data (CEMS GLOFAS)                                                                                                         
    FLOOD_RISK_DATASET = "cems-glofas-historical"

    FLOOD_RISK_VARIABLES = [
        "river_discharge_in_the_last_24_hours",
        "runoff_water_equivalent",
        "snow_depth_water_equivalent",
        "soil_wetness_index",
    ]

    FLOOD_RISK_REQUEST = {
        "system_version": ["version_4_0"],
        "hydrological_model": ["lisflood"],
        "product_type": ["consolidated"],
        "variable": FLOOD_RISK_VARIABLES,
        "hyear": FLOOD_DATA_PERIOD,
        "hmonth": [f"{month:02d}" for month in range(1, 13)],
        "hday": ["01"],
        "data_format": "netcdf",
        "download_format": "zip",
        "area": [71, -25, 35, 45],  # Europe region
    }

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
            "month": [f"{month:02d}" for month in range(1, 13)],
            "area": [71, -25, 35, 45],  # Europe region
        }
