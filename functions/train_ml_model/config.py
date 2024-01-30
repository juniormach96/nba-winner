import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    S3_BUCKET: str = os.getenv("S3_BUCKET")
    TRAIN_FILE_NAME: str = os.getenv("TRAIN_FILE_NAME")
    ML_MODEL_FILE: str = os.getenv("ML_MODEL_FILE")


config = AppConfig()
