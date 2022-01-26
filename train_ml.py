from typing import List
import pandas as pd
from pycaret.classification import *
from prefect import task, Flow
from typing import List


@task
def split_df() -> List[pd.DataFrame]:
    # Read data
    games = pd.read_csv('data/games')
    # Split into train and test
    cutoff = round(games.shape[0]*0.75)
    train = games.loc[:cutoff]
    test = games.loc[cutoff:]
    return [train, test]


@task
def train_model(dfs: List[pd.DataFrame]) -> None:
    train = dfs[0]
    test = dfs[1]
    # Start experiment
    s = setup(
        train,
        test_data=test,
        target="WINNER",
        normalize=True,
        normalize_method="minmax",
        silent=True,
        remove_outliers=True,
        trigonometry_features=True,
        fold_strategy='timeseries',
        ignore_features=['GAME_ID', 'N_GAMES_HOME', 'N_GAMES_AWAY'],
        data_split_stratify=True)

    # Compare top 5 models
    best = compare_models(n_select=1, exclude=['lr', 'knn', 'nb'])
    # Select and tune the Best
    tuned_best = tune_model(
        best[0], search_library='optuna', search_algorithm='tpe')
    # Adjust probabilities
    calibrated = calibrate_model(tuned_best)
    # Train on the whole dataset
    final_model = finalize_model(calibrated)
    # Save model
    save_model(final_model, 'models/best_model')


def ml_flow():
    with Flow(name='nba_etl_pipeline') as flow:
        dfs = split_df()
        train_model(dfs)
    return flow


if __name__ == '__main__':
    flow = ml_flow()
    flow.run()
