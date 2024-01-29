import json
from datetime import date
from typing import List

import numpy as np
import pandas as pd
from prefect import task

from .config import config


@task
def pre_select_features(games: pd.DataFrame) -> pd.DataFrame:
    features = config.PRE_SELECTED_FEATURES
    return games[features]


@task
def drop_few_games_teams(games: pd.DataFrame) -> pd.DataFrame:
    # Find how many games each team has played
    # And sort by the GAME_DATE
    n_games = (
        games.groupby("TEAM_NAME")
        .agg({"TEAM_NAME": "count"})
        .rename({"TEAM_NAME": "N_GAMES"}, axis=1)
        .reset_index()
    )

    games = pd.merge(games, n_games, on="TEAM_NAME", how="left").sort_values(
        "GAME_DATE"
    )
    # Exclude teams with few games
    return games[games["N_GAMES"] > config.MIN_GAMES_PER_TEAM]


@task
def add_moving_average(games: pd.DataFrame) -> pd.DataFrame:
    # Add empty line at bottom to receive moving average values
    # from previous columns
    for team in games.TEAM_NAME.unique():
        games = games.append(
            {"TEAM_NAME": team, "GAME_DATE": date.today().strftime("%Y-%m-%d")},
            ignore_index=True,
        )

    # Filter numerical columns to not iterate over unnecessary columns
    num_cols = list(games.select_dtypes("number").columns)
    # Exclude columns you don't want to iterate over
    exclude = ["N_GAMES"]
    num_cols = [col for col in num_cols if col not in exclude]
    # Add TEAM_NAME to group by it
    num_cols.append("TEAM_NAME")
    # Add moving average dinamically
    for window in config.MOVING_AVERAGE_WINDOWS:
        for col in num_cols:
            if col != "TEAM_NAME":
                games[f"avg_last_{window}_{col}"] = games.groupby("TEAM_NAME")[
                    col
                ].transform(lambda x: x.rolling(window, closed="left").mean())
    return games


@task
def separate_bottom_games(games: pd.DataFrame) -> List[pd.DataFrame]:
    # Separate Bottom Games to use them on prediction
    to_predict = games.tail(len(games.TEAM_NAME.unique()))
    print(to_predict)
    # Drop nulls (early season games and bottom ones)
    games.dropna(inplace=True)
    return [games, to_predict]
