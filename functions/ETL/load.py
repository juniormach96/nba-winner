import os
from io import StringIO
from typing import List

import boto3
import pandas as pd
from prefect import task


@task
def load(dfs: List[pd.DataFrame]) -> None:
    s3_bucket = os.environ.get("S3_BUCKET")
    if not s3_bucket:
        raise ValueError("S3_BUCKET environment variable not set")

    s3_client = boto3.client("s3")

    # Convert DataFrame to CSV in memory
    csv_buffer_games = StringIO()
    dfs[0].to_csv(csv_buffer_games, index=False)
    csv_buffer_games.seek(0)  # Rewind the buffer

    csv_buffer_to_predict = StringIO()
    dfs[1].to_csv(csv_buffer_to_predict, index=False)
    csv_buffer_to_predict.seek(0)  # Rewind the buffer

    # Upload to S3
    s3_client.put_object(
        Bucket=s3_bucket, Key="games.csv", Body=csv_buffer_games.getvalue()
    )
    s3_client.put_object(
        Bucket=s3_bucket, Key="to_predict.csv", Body=csv_buffer_to_predict.getvalue()
    )
