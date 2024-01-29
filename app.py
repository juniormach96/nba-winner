#!/usr/bin/env python3
import aws_cdk as cdk

from cdk.etl_lambda_s3 import ETLLambdaS3

app = cdk.App()
ETLLambdaS3(
    app,
    "ETLLambdaS3",
)

app.synth()
