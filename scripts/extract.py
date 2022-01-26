from prefect import task
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder


@task
def extract() -> pd.DataFrame:
    gamefinder = leaguegamefinder.LeagueGameFinder(
        date_from_nullable='01/01/2018',  # MM/DD/YYYY format
        league_id_nullable='00'  # NBA Games only
    )
    games = gamefinder.get_data_frames()
    if not games:
        raise Exception('No data fetched!')
    return games[0]
