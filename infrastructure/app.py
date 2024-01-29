#!/usr/bin/env python3
import aws_cdk as cdk

from cdk.s3_object_lambda_chain import S3ObjectLambdaStack

app = cdk.App()
S3ObjectLambdaStack(
    app,
    "S3ObjectLambdaStack",
)

app.synth()
