import os
import pickle
from io import StringIO

import boto3
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from skopt import gp_minimize
from skopt.space import Integer

from config import config

s3_client = boto3.client("s3")


def read_data_from_s3(bucket, file_name):
    csv_obj = s3_client.get_object(Bucket=bucket, Key=file_name)
    body = csv_obj["Body"]
    csv_string = body.read().decode("utf-8")

    df = pd.read_csv(StringIO(csv_string))
    return df


def train_model(X_train, y_train, params={}):
    model = RandomForestRegressor(**params)
    model.fit(X_train, y_train)
    return model


def time_series_split(
    df, cutoff_ratio=0.75, target_columns=config.TARGET, feature_columns=config.FEATURES
):
    cutoff = int(len(df) * cutoff_ratio)

    train_df = df.iloc[:cutoff]
    test_df = df.iloc[cutoff:]

    X_train = train_df[feature_columns]
    y_train = train_df[target_columns]
    X_test = test_df[feature_columns]
    y_test = test_df[target_columns]

    return X_train, X_test, y_train, y_test


def optimize_model(X, y, n_calls=config.N_CALLS_OPTIMIZATION):
    def objective(params):
        model = RandomForestRegressor(
            n_estimators=params[0],
            max_depth=params[1],
            min_samples_split=params[2],
            min_samples_leaf=params[3],
            random_state=0,
        )
        time_series_cv = TimeSeriesSplit(n_splits=5)
        return -np.mean(
            cross_val_score(
                model, X, y, cv=time_series_cv, scoring="neg_mean_squared_error"
            )
        )

    search_space = [
        Integer(100, 1000, name="n_estimators"),
        Integer(5, 50, name="max_depth"),
        Integer(2, 10, name="min_samples_split"),
        Integer(1, 10, name="min_samples_leaf"),
    ]

    result = gp_minimize(objective, search_space, n_calls=n_calls, random_state=0)

    best_params = {
        "n_estimators": result.x[0],
        "max_depth": result.x[1],
        "min_samples_split": result.x[2],
        "min_samples_leaf": result.x[3],
    }

    return best_params


def get_base_path():
    if os.getenv("LOCAL_TEST"):
        # Running locally
        return "."
    else:
        # Running in AWS Lambda
        return "/tmp"


def upload_model_to_s3(model, bucket, model_key):
    # Serialize the model
    model_data = pickle.dumps(model)

    # Determine the base path
    base_path = get_base_path()
    temp_path = os.path.join(base_path, model_key)

    # Write to a file
    with open(temp_path, "wb") as file:
        file.write(model_data)

    # Upload the file to S3
    with open(temp_path, "rb") as file:
        s3_client.upload_fileobj(file, bucket, model_key)


def handler(event, context):
    # Read data from S3
    df = read_data_from_s3(config.S3_BUCKET, config.TRAIN_FILE_NAME)
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = time_series_split(df)
    # Optimize model
    optimized_params = optimize_model(X_train, y_train)
    # Train model with optimized parameters
    X = df[config.FEATURES]
    y = df[config.TARGET]
    model = train_model(X, y, params=optimized_params)
    # Upload model to S3
    upload_model_to_s3(model, config.S3_BUCKET, config.ML_MODEL_FILE)


if __name__ == "__main__":
    # For local test
    if os.getenv("LOCAL_TEST"):
        handler({}, None)
