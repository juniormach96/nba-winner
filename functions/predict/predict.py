import os
import json
import pickle
from io import BytesIO
import numpy as np
import pandas as pd
import boto3
from sklearn.metrics import mean_squared_error
from sklearn.base import clone  # Used to copy the original model

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

def calculate_rmse(predictions, actuals):
    mse = mean_squared_error(actuals, predictions)
    return np.sqrt(mse)

def build_response(response_body):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": response_body,
    }

def handler(event, context):
    bucket = config.S3_BUCKET
    model_key = config.ML_MODEL_FILE
    dataframe_key = config.PREDICT_FILE_NAME
    train_file_key = config.TRAIN_FILE_NAME
    features = config.FEATURES
    target_columns = config.TARGET

    # Load the original model (fully trained)
    original_model = load_model_from_s3(bucket, model_key)
    df = load_dataframe_from_s3(bucket, dataframe_key)
    teams_df = df[["home_team_abbreviation", "away_team_abbreviation"]]
    train_df = load_dataframe_from_s3(bucket, train_file_key)

    # Manually split the training data for time series (75% for training, 25% for testing)
    split_index = int(len(train_df) * 0.75)
    train_data = train_df[:split_index]
    test_data = train_df[split_index:]

    # Use a copy of the original model for retraining
    retrain_model = clone(original_model)

    # Retrain the model on the first 75% of the training data
    new_target = train_data[target_columns]#.sum(axis=1)
    retrain_model.fit(train_data[features], new_target)

    # Calculate predictions and RMSE on the last 25% test data
    test_actuals = test_data[target_columns].sum(axis=1)
    test_predictions = retrain_model.predict(test_data[features]).sum(axis=1)#
    test_rmse = calculate_rmse(test_predictions, test_actuals)

    # Use the original model to predict new data
    new_predictions = original_model.predict(df[features])

    results = []
    for i, prediction in enumerate(new_predictions):
        home_team = teams_df.iloc[i]["home_team_abbreviation"]
        away_team = teams_df.iloc[i]["away_team_abbreviation"]
        result = {
            home_team: prediction[0],
            away_team: prediction[1],
            "sum_result": prediction[0] + prediction[1],
            "match": f"{home_team} vs {away_team}"
        }
        results.append(result)
    response_body = json.dumps({
        "predictions": results,
        "rmse": test_rmse
    })
    print(response_body)

    return build_response(response_body)

if __name__ == "__main__":
    if os.getenv("LOCAL_TEST"):
        handler({}, None)

