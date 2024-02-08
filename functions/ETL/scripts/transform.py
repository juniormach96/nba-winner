from datetime import datetime, timezone
from typing import Dict, List, Tuple

import pandas as pd
from config import config
from pandas import DataFrame
from prefect import task


def flatten_dict(
    d: List[Dict[str, any]], parent_key: str = "", sep: str = "_"
) -> Dict[str, any]:
    """Flattens a nested dictionary into a single-level dictionary with concatenated keys."""
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, Dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def pre_select_features(df: DataFrame) -> DataFrame:
    """Selects predefined features from the DataFrame."""
    features = config.PRE_SELECTED_FEATURES
    return df[features]


def correct_dtypes(df: DataFrame) -> DataFrame:
    """Converts 'date' column to datetime format."""
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize('UTC')
    return df


def duplicate_dataframe(df: DataFrame) -> Tuple[DataFrame, DataFrame]:
    """Duplicates the DataFrame for home and away teams with appropriate renaming."""
    home_teams_df = df.rename(
        {
            "home_team_abbreviation": "team_abbreviation",
            "visitor_team_abbreviation": "opponent_team_abbreviation",
            "home_team_score": "team_score",
            "visitor_team_score": "opponent_score",
        },
        axis=1,
    )
    away_teams_df = df.rename(
        {
            "visitor_team_abbreviation": "team_abbreviation",
            "home_team_abbreviation": "opponent_team_abbreviation",
            "visitor_team_score": "team_score",
            "home_team_score": "opponent_score",
        },
        axis=1,
    )
    home_teams_df["is_home"] = 1
    away_teams_df["is_home"] = 0
    return home_teams_df, away_teams_df


def join_and_sort_dataframes(
    home_teams_df: DataFrame, away_teams_df: DataFrame
) -> DataFrame:
    """Joins and sorts the home and away team DataFrames."""
    return pd.concat([home_teams_df, away_teams_df], axis=0).sort_values(["date", "id"])


def calculate_moving_average_of_num_columns(df: DataFrame) -> DataFrame:
    """Calculates moving averages for numeric columns."""

    def select_cols_to_iterate(df: DataFrame) -> List[str]:
        num_cols = list(df.select_dtypes("number").columns)
        exclude_cols = ["is_home", "id", "date"]
        return [col for col in num_cols if col not in exclude_cols]

    cols_to_iterate = select_cols_to_iterate(df)
    for window in config.MOVING_AVERAGE_WINDOWS:
        for col in cols_to_iterate:
            if col not in (config.TEAM_NAME_COLUMN, config.OPPONENT_TEAM_COLUMN):
                df[f"avg_last_{window}_{col}"] = df.groupby(config.TEAM_NAME_COLUMN)[
                    col
                ].transform(lambda x: x.rolling(window, closed="left").mean())
    return df


def put_games_on_single_row(df: DataFrame) -> DataFrame:
    """Merges home and away team data into a single row per game."""
    home_teams_df = df[df["is_home"] == 1]
    away_teams_df = df[df["is_home"] == 0]
    home_teams_df = home_teams_df.rename(
        columns=lambda x: "home_" + x if x != "id" else x
    )
    away_teams_df = away_teams_df.rename(
        columns=lambda x: "away_" + x if x != "id" else x
    )
    return pd.merge(home_teams_df, away_teams_df, on="id")


def remove_unnecessary_columns(df: DataFrame) -> DataFrame:
    """Keeps only the necessary columns in the DataFrame."""
    features = [
        "id",
        "home_date",
        "home_team_abbreviation",
        "away_team_abbreviation",
        "home_team_score",
        "away_team_score",
        "home_avg_last_5_team_score",
        "home_avg_last_5_opponent_score",
        "home_avg_last_10_team_score",
        "home_avg_last_10_opponent_score",
        "home_avg_last_15_team_score",
        "home_avg_last_15_opponent_score",
        "home_avg_last_20_team_score",
        "home_avg_last_20_opponent_score",
    ]
    return df[features]


def separate_games_to_train_and_predict(df: DataFrame) -> Tuple[DataFrame, DataFrame]:
    """Separates the games into those to train on and those to predict."""
    today_utc = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    n_teams = len(df["home_team_abbreviation"].unique())

    to_predict = df[
        (df["home_date"] >= today_utc)
        & (df["home_team_score"] == 0)
        & (df["away_team_score"] == 0)
    ].head(n_teams//2)
    to_train = df[(df["home_team_score"] != 0) & (df["away_team_score"] != 0)].dropna()
    return to_train, to_predict


@task
def transform(games_data: List[Dict[str, any]]) -> Tuple[DataFrame, DataFrame]:
    """Transforms the DataFrame through a series of predefined steps."""
    flattened_games = [flatten_dict(game) for game in games_data]
    df = pd.DataFrame(flattened_games)
    df = pre_select_features(df)
    df = correct_dtypes(df)
    home_teams_df, away_teams_df = duplicate_dataframe(df)
    df = join_and_sort_dataframes(home_teams_df, away_teams_df)
    df = calculate_moving_average_of_num_columns(df)
    df = put_games_on_single_row(df)
    df = remove_unnecessary_columns(df)
    to_train, to_predict = separate_games_to_train_and_predict(df)
    return to_train, to_predict
