from typing import Dict, List, Optional

import requests
from config import config
from prefect import task


def fetch_games(start_date: str, end_date: str = None, per_page: int = 100) -> list:
    base_url = config.BASE_NBA_URL
    games = []
    page = 0

    while True:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "per_page": per_page,
            "page": page,
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        games.extend(data["data"])

        if data["meta"]["next_page"] is None:
            break
        page += 1

    return games


@task
def extract(
    start_date: str = config.START_DATE, end_date: Optional[str] = None
) -> List[Dict[str, any]]:
    return fetch_games(start_date, end_date)
