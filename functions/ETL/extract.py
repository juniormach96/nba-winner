import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from prefect import task

from .config import config


@task
def extract() -> pd.DataFrame:
    gamefinder = leaguegamefinder.LeagueGameFinder(
        date_from_nullable=config.START_DATE, league_id_nullable=config.NBA_LEAGUE_ID  # NBA Games only
    )
    games = gamefinder.get_data_frames()
    if not games:
        raise Exception("No data fetched!")
    return games[0]
