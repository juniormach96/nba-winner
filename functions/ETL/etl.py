import os

from prefect import Flow

from scripts.extract import extract
from scripts.load import load
from scripts.transform import transform


def prefect_flow():
    with Flow(name="nba_etl_pipeline") as flow:
        games_data = extract()
        to_train, to_predict = transform(games_data)
        load(to_train, file_name="to_train")
        load(to_predict, file_name="to_predict")

    return flow


def handler(event, context):
    prefect_flow().run()


if __name__ == "__main__":
    # For local test
    if os.getenv("LOCAL_TEST"):
        handler({}, None)
