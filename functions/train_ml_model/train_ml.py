import os
from io import StringIO

import boto3
import pandas as pd
from joblib import dump
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from skopt import gp_minimize
from skopt.space import Integer, Real

from .config import config

s3_client = boto3.client("s3")


def read_data_from_s3(bucket, file_name):
    csv_obj = s3_client.get_object(Bucket=bucket, Key=file_name)
    body = csv_obj["Body"]
    csv_string = body.read().decode("utf-8")

    df = pd.read_csv(StringIO(csv_string))
    return df


def train_model(X_train, y_train, params):
    model = LGBMRegressor(**params)
    model.fit(X_train, y_train)
    return model


def optimize_model(X_train, y_train):
    def objective(params):
        model = LGBMRegressor(**params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        return mean_squared_error(y_test, y_pred)

    # Define the space of hyperparameters to search
    search_space = [
        Integer(100, 1000, name="n_estimators"),
        Real(0.01, 0.5, name="learning_rate"),
        Integer(1, 30, name="max_depth"),
        Real(0.1, 1.0, name="subsample"),
        Real(0.1, 1.0, name="colsample_bytree"),
    ]

    result = gp_minimize(objective, search_space, n_calls=20, random_state=0)

    # Extract the best parameters
    best_params = {
        dimension.name: result.x[i] for i, dimension in enumerate(search_space)
    }
    return best_params


def upload_model_to_s3(model, bucket, model_file):
    dump(model, config.ML_MODEL_FILE)
    s3_client.upload_file(config.ML_MODEL_FILE, bucket, model_file)


def handler(event, context):
    # Read data from S3
    df = read_data_from_s3(config.BUCKET_NAME, config.TRAIN_FILE_NAME)
    # Preprocess data (add your preprocessing logic here)
    X = df.drop("target_column", axis=1)
    y = df["target_column"]
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # Optimize model
    # optimized_params = optimize_model(X_train, y_train)
    # Train model with optimized parameters
    model = train_model(X_train, y_train)
    # Upload model to S3
    upload_model_to_s3(model, config.BUCKET_NAME, config.ML_MODEL_FILE)
    # Clean up local model file
    os.remove(config.ML_MODEL_FILE)


if __name__ == "__main__":
    # For local test
    if os.getenv("LOCAL_TEST"):
        handler({}, None)
