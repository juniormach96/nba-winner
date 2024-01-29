from prefect import Flow

from .extract import extract
from .load import load
from .transform import (
    add_moving_average,
    drop_few_games_teams,
    pre_select_features,
    separate_bottom_games,
)


def prefect_flow():
    with Flow(name="nba_etl_pipeline") as flow:
        games = extract()
        games = pre_select_features(games)
        games = drop_few_games_teams(games)
        dfs = add_moving_average(games)
        dfs = separate_bottom_games(dfs)
        load()

    return flow


def handler(event, context):
    prefect_flow().run()
