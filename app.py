#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.codebuild_stack import CodeBuildStack
from stacks.etl_stack import ETLStack
from stacks.predict_stack import PredictStack
from stacks.source_stack import SourceStack
from stacks.train_ml_stack import TrainMLStack

app = cdk.App()

source_stack = SourceStack(app, "SourceStack")

s3_bucket = source_stack.s3_bucket
codecommit_repository = source_stack.codecommit_repository

ecr_repositories = {
    "etl": source_stack.etl_ecr_repository,
    "train_ml": source_stack.train_ml_ecr_repository,
    "predict": source_stack.predict_ecr_repository,
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
    s3_bucket=s3_bucket,
    train_ml_ecr_repository=ecr_repositories["train_ml"],
)

predict_stack = PredictStack(
    app,
    "PredictStack",
    s3_bucket=s3_bucket,
    predict_ecr_repository=ecr_repositories["predict"],
)

lambda_functions = {
    "etl": etl_stack.etl_lambda_function,
    "train_ml": train_ml_stack.train_ml_lambda_function,
    "predict": predict_stack.predict_lambda_function,
}

codebuild_stack = CodeBuildStack(
    app,
    "CodeBuildStack",
    codecommit_repository=codecommit_repository,
    ecr_repositories=ecr_repositories,
    lambda_functions=lambda_functions,
)

app.synth()
