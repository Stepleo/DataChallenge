import zipfile
import tempfile
import os

import pandas as pd
import numpy as np
import xarray as xr
import psutil

from data_config import DataConfig

def load_data():
    """
    Load the precipitation dataset and creates a categorical variable for the risk of flooding.
    Load the historical data and join it to the created categorical variable.
    Load the projections data in the same manner but do not join the categorical variable.
    Ultimately return the historical + categorical variable (training) and the projections data (inference).
    """

    print("Loading datasets into dataframes...", end="", flush=True)
    precipitation_df = load_precipitation_data()
    print(f"Precipitation data loaded with {len(precipitation_df)} samples.")
    categorical_data = create_categorical_variable(precipitation_df)
    
    print(f"Categorical data created with {len(categorical_data)} samples.")

    historical_df = load_projection_data("historical")

    train_df = historical_df.join(categorical_data, how="inner")
    print(f"Training set loaded with {len(train_df)} samples.")

    
    
    ssp1_df = load_projection_data("ssp1_2_6")  # Low emissions
    ssp2_df = load_projection_data("ssp2_4_5")  # Medium emissions
    ssp5_df = load_projection_data("ssp5_8_5")  # High emissions

    print(f"SSP1 set loaded with {len(ssp1_df)} samples.")
    print(f"SSP2 set loaded with {len(ssp2_df)} samples.")
    print(f"SSP5 set loaded with {len(ssp5_df)} samples.")
    
    flood_risk_df = load_flood_risk_data()
    
    print(f"Flood risk set loaded with {len(flood_risk_df)} samples.")

    return train_df, ssp1_df, ssp2_df, ssp5_df, flood_risk_df

def load_precipitation_data():
    """
    Goes into the zip file and loads the precipitation data for each variable for each year
    and merge everything into a single dataframe.
    """
    precipitation_df = pd.DataFrame()
    for variable, variable_name in DataConfig.EXTREME_PRECIPITATION_VARIABLES.items():
        print(f"Loading {variable_name} data...")
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
            with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
                temp_file_path = tmp_file.name

                # Open the ZIP file
                with zipfile.ZipFile(zip_path, 'r') as z:
                    #check if the file is in the zip
                    if file_name not in z.namelist():
                        print(f"{file_name} not found in the zip !")
                        continue
                    # Extract the file inside the ZIP to the temporary file
                    with z.open(file_name) as f:
                        tmp_file.write(f.read())

                # Load the NetCDF file with xarray
                dataset = xr.open_dataset(temp_file_path, engine='netcdf4').to_dataframe()

                dataset.columns = [variable]

                variable_df_list.append(dataset.reset_index())


        # Concatenate all yearly data for the current variable
        variable_df = pd.concat(variable_df_list).dropna()
        variable_df = easier_coordinates(variable_df)
   

        # Merge the data for all variables
        if precipitation_df.empty:
            precipitation_df = variable_df
        else:
            precipitation_df = precipitation_df.merge(variable_df, on=['time', 'latitude', 'longitude'], how='outer')
            
        print_memory_usage(f"Loaded {variable_name} data.")
    return precipitation_df

def print_memory_usage(message):
    """Print the current memory usage with a custom message."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"{message} Memory usage: {mem_info.rss / (1024 ** 2):.2f} MB")
    
    
def load_projection_data(experiment):
    """
    Goes into the zip file and loads the projections data for each variable for each year
    and merge everything into a single dataframe.
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

def load_flood_risk_data():
    """
    Goes into the zip files and loads the flood risk data for each variable for each year
    and merge everything into a single dataframe.
    """
    flood_risk_df = pd.DataFrame()
    year_df_list = []
    for start_year in range(2000, 2025, 1):
        end_year = min(start_year + 0, 2024)
        file_name = f"flood_risk_{start_year}_{end_year}.zip"
        zip_path = DataConfig.DATA_PATH / file_name

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            temp_file_path = tmp_file.name

            # Open the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Extract only the .nc files inside the ZIP to the temporary directory
                for file_info in z.infolist():
                    if file_info.filename.endswith('.nc'):
                        with z.open(file_info.filename) as f:
                            tmp_file.write(f.read())
            
            print(f"extracted zip file {zip_path}")

            # Load the NetCDF files with xarray
            dataset = xr.open_dataset(
                os.path.join(temp_file_path),
                engine='netcdf4',
            ).to_dataframe().reset_index()

            #rename valid_time column to time to match the other datasets
            dataset = dataset.rename(columns={"valid_time": "time"})
            dataset = easier_coordinates(dataset.dropna())

            year_df_list.append(dataset)

            os.remove(temp_file_path)

        # Concatenate all yearly data for the current variable
        variable_df = pd.concat(year_df_list).dropna()

    # Merge the data for all variables
    if flood_risk_df.empty:
        flood_risk_df = variable_df
    else:
        flood_risk_df = flood_risk_df.merge(variable_df, on=['time', 'latitude', 'longitude'], how='outer')

    # Save the flood risk data to a CSV file
    flood_risk_df.to_csv(DataConfig.DATA_PATH / 'flood_risk_data.csv', index=False)

    return flood_risk_df

def create_categorical_variable(precipitation_df):
    """
    Create a categorical variable for the risk of flooding based on the precipitation data.
    A row is classified as 'high' if it is above the 50th percentile in all variables.
    """
    # Calculate the 50th percentile for each variable
    percentiles = precipitation_df.quantile(0.50)

    # Initialize the categorical data with 'low'
    categorical_data = pd.DataFrame(index=precipitation_df.index)
    categorical_data["target"] = "low"

    # Check if all variables are above their respective 50th percentile
    above_percentile = (precipitation_df > percentiles).all(axis=1)

    # Classify as 'high' if all conditions are met
    categorical_data.loc[above_percentile, "target"] = "high"

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
