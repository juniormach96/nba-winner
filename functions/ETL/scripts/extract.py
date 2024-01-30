from collections.abc import MutableMapping
from typing import Optional

import pandas as pd
import requests
from config import config
from prefect import task


def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '_') -> MutableMapping:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def fetch_games(start_date: str, end_date: str = None, per_page: int = 100) -> list:
    base_url = config.BASE_NBA_URL
    games = []
    page = 0

    while True:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "per_page": per_page,
            "page": page
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        games.extend(data['data'])

        if data['meta']['next_page'] is None:
            break
        page += 1

    return games

@task
def extract(start_date: str = config.START_DATE, end_date: Optional[str] = None) -> pd.DataFrame:
    games_data = fetch_games(start_date, end_date)
    flattened_games = [flatten_dict(game) for game in games_data]
    return pd.DataFrame(flattened_games)
