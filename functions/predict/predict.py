import os
import pickle
from io import BytesIO

import boto3
import pandas as pd

from config import config

s3_client = boto3.client("s3")


def load_model_from_s3(bucket, model_key):
    response = s3_client.get_object(Bucket=bucket, Key=model_key)
    model_str = response["Body"].read()
    return pickle.loads(model_str)


def load_dataframe_from_s3(bucket, file_key):
    response = s3_client.get_object(Bucket=bucket, Key=file_key)
    df_str = response["Body"].read()
    return pd.read_csv(BytesIO(df_str))


def handler(event, context):
    bucket = config.S3_BUCKET
    model_key = config.ML_MODEL_FILE
    dataframe_key = config.PREDICT_FILE_NAME
    features = config.FEATURES

    # Load model and dataframe
    model = load_model_from_s3(bucket, model_key)
    df = load_dataframe_from_s3(bucket, dataframe_key)

    # Assuming 'home_team_abbreviation' and 'away_team_abbreviation' are column names in df
    # Extract these columns for response
    teams_df = df[["home_team_abbreviation", "away_team_abbreviation"]]

    # Extract features for prediction
    to_predict_df = df[features]

    # Perform prediction
    predictions = model.predict(to_predict_df)

    # Combine predictions with team abbreviations
    results = []
    for i, prediction in enumerate(predictions):
        result = {
            teams_df.iloc[i]["home_team_abbreviation"]: prediction[0],
            teams_df.iloc[i]["away_team_abbreviation"]: prediction[1],
        }
        results.append(result)
    print(results)
    return results


if __name__ == "__main__":
    if os.getenv("LOCAL_TEST"):
        handler({}, None)
