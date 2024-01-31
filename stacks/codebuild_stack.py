from typing import Dict, List

from aws_cdk import App, Aws, CfnOutput, Duration, Stack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as pipeline_actions
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda


class CodeBuildStack(Stack):
    def __init__(
        self,
        scope: App,
        id: str,
        codecommit_repository: codecommit.Repository,
        ecr_repositories: Dict[str, ecr.Repository],
        lambda_functions: Dict[str, _lambda.Function],
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.codebuild_project = self.create_codebuild_project(
            codecommit_repository,
            ecr_repositories=ecr_repositories,
            lambda_functions=lambda_functions,
        )

    def create_codebuild_project(
        self,
        codecommit_repository: codecommit.Repository,
        ecr_repositories: Dict[str, ecr.Repository],
        lambda_functions: Dict[str, _lambda.Function],
    ):
        codebuild_source = codebuild.Source.code_commit(
            repository=codecommit_repository,
            branch_or_ref="main",
        )
        codebuild_environment = codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
            privileged=True,  # Necessary for building Docker images
        )
        codebuild_environment_variables = {
            "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(value=Aws.ACCOUNT_ID),
            "REGION": codebuild.BuildEnvironmentVariable(value=Aws.REGION),
            # ETL
            "ETL_IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
            "ETL_IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                value=ecr_repositories["etl"].repository_name
            ),
            "ETL_LAMBDA_FUNCTION_NAME": codebuild.BuildEnvironmentVariable(
                value=lambda_functions["etl"].function_name
            ),
            # TRAIN ML
            "TRAIN_ML_IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
            "TRAIN_ML_IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                value=ecr_repositories["train_ml"].repository_name
            ),
            "TRAIN_ML_LAMBDA_FUNCTION_NAME": codebuild.BuildEnvironmentVariable(
                value=lambda_functions["train_ml"].function_name
            ),
            # PREDICT
            "PREDICT_IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
            "PREDICT_IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                value=ecr_repositories["predict"].repository_name
            ),
            "PREDICT_LAMBDA_FUNCTION_NAME": codebuild.BuildEnvironmentVariable(
                value=lambda_functions["predict"].function_name
            ),
        }
        build_project = codebuild.Project(
            self,
            "ETLBuildProject",
            source=codebuild_source,
            environment=codebuild_environment,
            environment_variables=codebuild_environment_variables,
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
        )

        for ecr_repository in ecr_repositories.values():
            ecr_repository.grant_pull_push(build_project)

        # Add permissions to update Lambda function code
        build_project.add_to_role_policy(
            iam.PolicyStatement(
                actions=["lambda:UpdateFunctionCode"],
                resources=[
                    lambda_function.function_arn
                    for lambda_function in lambda_functions.values()
                ],
            )
        )
        # Add ECR permissions to the CodeBuild project role
        build_project.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetAuthorizationToken",
                ],
                resources=[
                    ecr_repository.repository_arn
                    for ecr_repository in ecr_repositories.values()
                ],
            )
        )
        return build_project
