import os
import cdsapi
from sklearn.model_selection import train_test_split

from data_config import DataConfig, ProjectionRequest
from data_proprocessing import load_data

def download_flood_risk_data(client, dataset_name, request_params, save_path_template):
    """Download flood risk data in chunks to avoid large requests."""
    years_per_request = 10  # Adjust this number based on the API limitations
    years = request_params["hyear"]

    for i in range(0, len(years), years_per_request):
        chunk_years = years[i:i + years_per_request]
        chunk_request = request_params.copy()
        chunk_request["hyear"] = chunk_years

        # Convert Path object to string before formatting
        save_path = str(save_path_template).format(start_year=chunk_years[0], end_year=chunk_years[-1])

        if os.path.exists(save_path):
            print(f"{dataset_name} data for years {chunk_years[0]}-{chunk_years[-1]} already exists.")
        else:
            print(f"Downloading {dataset_name} data for years {chunk_years[0]}-{chunk_years[-1]}...")
            client.retrieve(dataset_name, chunk_request, save_path)
            print(f"Download completed: {dataset_name} for years {chunk_years[0]}-{chunk_years[-1]}")

if __name__ == "__main__":
    if not DataConfig.DATA_PATH.exists():
        DataConfig.DATA_PATH.mkdir()

    # Initialize CDS API client
    client = cdsapi.Client()

    # Function to download dataset if it doesn't exist
    def download_dataset(dataset_name, request_params, save_path):
        """Download dataset from Copernicus Climate Data Store if not already present."""
        if os.path.exists(save_path):
            print(f"{dataset_name} data already exists.")
        else:
            print(f"Downloading {dataset_name} data...")
            client.retrieve(dataset_name, request_params, save_path)
            print(f"Download completed: {dataset_name}")

    ## Step 1: Download Precipitation Data
    precipitation_target = DataConfig.DATA_PATH / "precipitation.zip"
    download_dataset(
        DataConfig.EXTREME_PRECIPITATION_DATASET,
        DataConfig.EXTREME_PRECIPITATION_REQUEST,
        precipitation_target
    )

    ## Step 2: Download Flood Risk Data (CEMS GLOFAS Historical)
    flood_risk_target_template = DataConfig.DATA_PATH / "flood_risk_{start_year}_{end_year}.zip"
    download_flood_risk_data(
        client,
        DataConfig.FLOOD_RISK_DATASET,
        DataConfig.FLOOD_RISK_REQUEST,
        flood_risk_target_template
    )

    ## Step 3: Download Climate Projections Data
    for experiment in DataConfig.PROJECTIONS_EXPERIMENTS:
        period = (
            DataConfig.HISTORICAL_PERIOD
            if experiment == "historical"
            else DataConfig.PROJECTIONS_PERIOD
        )

        for variable in DataConfig.PROJECTIONS_VARIABLES:
            for model in DataConfig.PROJECTIONS_MODELS:
                projections_target = DataConfig.DATA_PATH / f"{experiment}_{variable}_{model}.zip"

                if os.path.exists(projections_target):
                    print(f"{experiment} {variable} {model} data already exists.")
                    continue

                projections_request = ProjectionRequest(
                    model, variable, experiment, period
                ).get_request()

                download_dataset(
                    DataConfig.PROJECTIONS_DATASET,
                    projections_request,
                    projections_target
                )

    print("✅ All datasets downloaded successfully.")

    ## Step 4: Load and Save Dataframes
    print("Loading datasets into dataframes...", end="", flush=True)
    train_df, ssp1_df, ssp2_df, ssp5_df, flood_risk_df = load_data()

    print("Splitting and saving datasets...", end="", flush=True)
    X_train, X_test = train_test_split(train_df, test_size=0.2, random_state=57, shuffle=True)

    # Save datasets
    X_train.to_csv(DataConfig.DATA_PATH / 'X_train.csv', index=False)
    X_test.to_csv(DataConfig.DATA_PATH / 'X_test.csv', index=False)
    ssp1_df.to_csv(DataConfig.DATA_PATH / 'ssp1_df.csv', index=False)
    ssp2_df.to_csv(DataConfig.DATA_PATH / 'ssp2_df.csv', index=False)
    ssp5_df.to_csv(DataConfig.DATA_PATH / 'ssp5_df.csv', index=False)

    # Save flood risk data
    flood_risk_df.to_csv(DataConfig.DATA_PATH / 'flood_risk_data.csv', index=False)

    print("✅ Data processing completed. All files saved successfully.")
