#!/usr/bin/env python3
import aws_cdk as cdk

from cdk.codebuild_stack import CodeBuildStack
from cdk.etl_stack import ETLStack
from cdk.source_stack import SourceStack
from cdk.train_ml_stack import TrainMLStack

app = cdk.App()

source_stack = SourceStack(app, "SourceStack")

s3_bucket = source_stack.s3_bucket

ecr_repositories = {
    "etl": source_stack.etl_ecr_repository,
    "train_ml": s3_bucket.train_ml_ecr_repository,
}

etl_stack = ETLStack(
    app,
    "ETLStack",
    s3_bucket=s3_bucket,
    etl_ecr_repository=ecr_repositories["etl"],
)

train_ml_stack = TrainMLStack(
    app,
    "TrainMLStack",
    s3_bucket=etl_stack.bucket,
    train_ml_ecr_repository=ecr_repositories["train_ml"],
)

lambda_functions = {
    "etl": etl_stack.etl_lambda_function,
    "train_ml": train_ml_stack.train_ml_lambda_function,
}

codebuild_stack = CodeBuildStack(
    app,
    "CodeBuildStack",
    ecr_repositories=ecr_repositories,
    lambda_functions=lambda_functions,
)

app.synth()
