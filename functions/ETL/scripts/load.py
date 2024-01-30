import os
from io import StringIO
from typing import List

import boto3
import pandas as pd
from prefect import task


@task
def load(df: pd.DataFrame, file_name: str) -> None:
    s3_bucket = os.environ.get("S3_BUCKET")
    if not s3_bucket:
        raise ValueError("S3_BUCKET environment variable not set")

    s3_client = boto3.client("s3")

    # Convert DataFrame to CSV in memory
    csv_buffer_games = StringIO()
    df.to_csv(csv_buffer_games, index=False)
    csv_buffer_games.seek(0)  # Rewind the buffer

    # Upload to S3
    s3_client.put_object(
        Bucket=s3_bucket, Key=f"{file_name}.csv", Body=csv_buffer_games.getvalue()
    )
