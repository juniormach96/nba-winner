from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class AppConfig:
    START_DATE: str = "01/01/2020"
    # NBA_LEAGUE_ID: str = "00"
    BASE_NBA_URL = "https://www.balldontlie.io/api/v1/games"
    PRE_SELECTED_FEATURES: List[str] = field(
        default_factory=lambda: [
            "id",
            "date",
            "home_team_abbreviation",
            "visitor_team_abbreviation",
            "home_team_score",
            "visitor_team_score",
        ]
    )
    MIN_GAMES_PER_TEAM: int = 100
    MOVING_AVERAGE_WINDOWS: List[int] = field(
        default_factory=lambda: [1, 5, 10, 15, 20]
    )
    TEAM_NAME_COLUMN: str = "team_abbreviation"
    OPPONENT_TEAM_COLUMN: str = "opponent_team_abbreviation"


config = AppConfig()
