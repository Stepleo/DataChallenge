import zipfile
import tempfile
import os

import pandas as pd
import numpy as np
import xarray as xr

from data_config import DataConfig

def load_data():
    """
    Load the precipitation dataset and creates a categorical variable for the risk of flooding.
    Load the historical data and join it to the created categorical variable.
    Load the projections data in the same manner but do not join the categorical variable.
    Ultimately return the historical + categorical variable (training) and the projections data (inference).
    """

    precipitation_df = load_precipitation_data()
    categorical_data = create_categorical_variable(precipitation_df)

    historical_df = load_projection_data("historical")

    train_df = historical_df.join(categorical_data, how="inner")

    ssp1_df = load_projection_data("ssp1_2_6")  # Low emissions
    ssp2_df = load_projection_data("ssp2_4_5")  # Medium emissions
    ssp5_df = load_projection_data("ssp5_8_5")  # High emissions

    return train_df, ssp1_df, ssp2_df, ssp5_df


def load_precipitation_data():
    """
    Goes into the zip file and loads the precipitation data for each variable for each year
    and merge evrything into a single dataframe.
    """
    precipitation_df = pd.DataFrame()
    for variable, variable_name in DataConfig.EXTREME_PRECIPITATION_VARIABLES.items():
        variable_df_list = []
        for year in DataConfig.HISTORICAL_PERIOD:
            file_name = (
                f"{variable_name}_europe_e-obs_monthly_99th_{year}_v1.nc"
                if "percentile" in variable_name
                else f"{variable_name}_europe_e-obs_monthly_{year}_v1.nc"
            )
            # Go fetch this file in the zip file
            zip_path = DataConfig.DATA_PATH / "precipitation.zip"
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                temp_file_path = tmp_file.name

                # Open the ZIP file
                with zipfile.ZipFile(zip_path, 'r') as z:
                    # Extract the file inside the ZIP to the temporary file
                    with z.open(file_name) as f:
                        tmp_file.write(f.read())

            # Load the NetCDF file with xarray
            dataset = xr.open_dataset(temp_file_path, engine='netcdf4').to_dataframe()

            dataset.columns = [variable]

            variable_df_list.append(dataset.reset_index())

            os.remove(temp_file_path)

        # Concatenate all yearly data for the current variable
        variable_df = pd.concat(variable_df_list).dropna()
        variable_df = easier_coordinates(variable_df)

        # Merge the data for all variables
        if precipitation_df.empty:
            precipitation_df = variable_df
        else:
            precipitation_df = precipitation_df.merge(variable_df, on=['time', 'latitude', 'longitude'], how='outer')

    return precipitation_df

def load_projection_data(experiment):
    """
    Goes into the zip file and loads the projections data for each variable for each year
    and merge evrything into a single dataframe.
    """
    projections_df = pd.DataFrame()
    for variable in DataConfig.PROJECTIONS_VARIABLES:
        for model in DataConfig.PROJECTIONS_MODELS:
            file_name = f"{experiment}_{variable}_{model}.zip"
            # Go fetch this file in the zip file
            zip_path = DataConfig.DATA_PATH / file_name
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                # Open the ZIP file
                with zipfile.ZipFile(zip_path, 'r') as z:
                    temp_file_path = tmp_file.name
                    # Extract only the .nc files inside the ZIP to the temporary directory
                    for file_info in z.infolist():
                        if file_info.filename.endswith('.nc'):
                            with z.open(file_info.filename) as f:
                                    tmp_file.write(f.read())

                # Load the NetCDF files with xarray
                dataset = xr.open_dataset(
                    os.path.join(temp_file_path),
                    engine='netcdf4',
                ).to_dataframe().reset_index()

                columns_to_keep = ['lat', 'lon', 'time', dataset.columns[-1]]
                dataset = dataset[columns_to_keep]
                dataset.columns = ["latitude", "longitude", "time", variable]
                dataset = dataset[["time", "latitude", "longitude", variable]]
                dataset = easier_coordinates(dataset.dropna())

                # Merge the data for all models
                if projections_df.empty:
                    projections_df = dataset
                else:
                    projections_df = projections_df.merge(dataset, on=['time', 'latitude', 'longitude'], how='outer')

                os.remove(temp_file_path)

    return projections_df

def create_categorical_variable(precipitation_df):
    """
    Create a categorical variable for the risk of flooding based on the precipitation data.
    """
    # TODO : This is a basic implementation but we'll need to put more thoughts into it
    categorical_data = pd.DataFrame(index=precipitation_df.index)
    categorical_data["risk_of_flooding"] = "low"
    for variable in DataConfig.EXTREME_PRECIPITATION_VARIABLES:
        if variable == "number_of_precipitation_days_exceeding_fixed_percentile":
            continue
        categorical_data.loc[
            precipitation_df[variable] > 0.95, "risk_of_flooding"
        ] = "high"

    return categorical_data

def easier_coordinates(dataframe):
    """
    Round the coordinates to the closest multiple of 5 to make them easier to work with and group.
    """
    dataframe["latitude"] = dataframe["latitude"].round()
    dataframe["longitude"] = dataframe["longitude"].round()
    dataframe["time"] = dataframe['time'].dt.to_period('M').dt.to_timestamp()

    # Aggregate the data that have the same coordinates now coordinates
    dataframe = dataframe.groupby(["time", "latitude", "longitude"]).mean().reset_index()

    return dataframe