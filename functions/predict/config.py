import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class AppConfig:
    S3_BUCKET: str = os.getenv("S3_BUCKET")
    PREDICT_FILE_NAME: str = os.getenv("PREDICT_FILE_NAME")
    ML_MODEL_FILE: str = os.getenv("ML_MODEL_FILE")
    FEATURES: List[str] = field(
        default_factory=lambda: [
            "home_avg_last_5_team_score",
            "home_avg_last_5_opponent_score",
            "home_avg_last_10_team_score",
            "home_avg_last_10_opponent_score",
            "home_avg_last_15_team_score",
            "home_avg_last_15_opponent_score",
            "home_avg_last_20_team_score",
            "home_avg_last_20_opponent_score",
        ]
    )


config = AppConfig()
