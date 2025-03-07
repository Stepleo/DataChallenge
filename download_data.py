import os

import cdsapi
from sklearn.model_selection import train_test_split

from data_config import DataConfig, ProjectionRequest
from data_proprocessing import load_data


if __name__ == "__main__":
    if not DataConfig.DATA_PATH.exists():
        DataConfig.DATA_PATH.mkdir()

    # Downloading the data if it does not exist
    print("Downloading the data...", end="", flush=True)
    client = cdsapi.Client()

    print("Loading the extreme precipitation data...", end="", flush=True)

    precipitation_target = DataConfig.DATA_PATH / "precipitation.zip"
    if os.path.exists(precipitation_target):
        print("The precipitation data already exists")
    else:
        precipitation_dataset = DataConfig.EXTREME_PRECIPITATION_DATASET
        precipitation_request = DataConfig.EXTREME_PRECIPITATION_REQUEST

        client.retrieve(
            precipitation_dataset, precipitation_request, precipitation_target
        )

    print("Loading the projection data...", end="", flush=True)

    for experiment in DataConfig.PROJECTIONS_EXPERIMENTS:
        period = (
            DataConfig.HISTORICAL_PERIOD
            if experiment == "historical"
            else DataConfig.PROJECTIONS_PERIOD
        )
        for variable in DataConfig.PROJECTIONS_VARIABLES:
            for model in DataConfig.PROJECTIONS_MODELS:
                print(
                    f"Loading the {experiment} {variable} {model} data...",
                    end="",
                    flush=True,
                )
                projections_target = DataConfig.DATA_PATH / f"{experiment}_{variable}_{model}.zip"
                if os.path.exists(projections_target):
                    print("The projection data already exists")
                    continue
                projections_request = ProjectionRequest(
                    model, variable, experiment, period
                ).get_request()
                projections_dataset = DataConfig.PROJECTIONS_DATASET
                client.retrieve(
                    projections_dataset, projections_request, projections_target
                )

    print("Done downloading the data", end="", flush=True)

    print("Loading the data into dataframes...", end="", flush=True)
    train_df, ssp1_df, ssp2_df, ssp5_df = load_data()

    # TODO : add a function to handle the data cleaning and preprocessing

    print("Saving the dataframes...", end="", flush=True)

    X_train, X_test = train_test_split(
        train_df, test_size=0.2, random_state=57, shuffle=True,
    )

    # Save the data
    X_train.to_csv(DataConfig.DATA_PATH / 'X_train.csv', index=False)
    X_test.to_csv(DataConfig.DATA_PATH / 'X_test.csv', index=False)

    ssp1_df.to_csv(DataConfig.DATA_PATH / 'ssp1_df.csv', index=False)
    ssp2_df.to_csv(DataConfig.DATA_PATH / 'ssp2_df.csv', index=False)
    ssp5_df.to_csv(DataConfig.DATA_PATH / 'ssp5_df.csv', index=False)
    print('done')
