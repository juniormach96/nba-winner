import os

from aws_cdk import App, Aws, CfnOutput, Stack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3


class ETLLambdaS3(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        self.codecommit_repository_name = "nba-etl-repository"
        codecommit_repository = self.create_codecommit_repository()
        ecr_repository = self.create_ecr_repository()
        bucket = self.create_bucket()
        etl_lambda_function = self.create_etl_lambda_function(bucket)
        self.create_codebuild_project(
            codecommit_repository, ecr_repository, etl_lambda_function
        )
        self.create_outputs(bucket, etl_lambda_function)

    def create_codecommit_repository(self):
        repository = codecommit.Repository.from_repository_name(
            self, "NbaEtlRepository", repository_name="nba-etl-repository"
        )
        return repository

    def create_ecr_repository(self):
        repository_name = "etl-lambda-repository"
        repository = ecr.Repository(self, "NewEcrRepo", repository_name=repository_name)
        return repository

    def create_codepipeline(self, codecommit_repository, codebuild_project):
        source_output = codepipeline.Artifact()

        pipeline = codepipeline.Pipeline(
            self,
            "ETLPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        cpactions.CodeCommitSourceAction(
                            action_name="CodeCommit_Source",
                            repository=codecommit_repository,
                            output=source_output,
                        )
                    ],
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        cpactions.CodeBuildAction(
                            action_name="Build_and_Push_Docker_Image",
                            project=codebuild_project,
                            input=source_output,
                        )
                    ],
                ),
            ],
        )
        return pipeline

    def create_codebuild_project(
        self, codecommit_repository, ecr_repository, etl_lambda_function
    ):
        build_project = codebuild.Project(
            self,
            "ETLBuildProject",
            source=codebuild.Source.code_commit(
                repository=codecommit_repository,
                branch_or_ref="main",  # Adjust the branch if necessary
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,  # Necessary for building Docker images
            ),
            environment_variables={
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(
                    value=Aws.ACCOUNT_ID
                ),
                "REGION": codebuild.BuildEnvironmentVariable(value=Aws.REGION),
                "IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
                "IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                    value=ecr_repository.repository_name
                ),
                "REPOSITORY_URI": codebuild.BuildEnvironmentVariable(
                    value=ecr_repository.repository_uri
                ),
                "LAMBDA_FUNCTION_NAME": codebuild.BuildEnvironmentVariable(
                    value=etl_lambda_function.function_name
                ),
            },
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
        )
        ecr_repository.grant_pull_push(build_project)
        return build_project

    def create_bucket(self):
        bucket = s3.Bucket(
            self,
            "nba-etl-bucket",
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
        return bucket

    def create_etl_lambda_function(self, bucket):
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[bucket.bucket_arn, bucket.arn_for_objects("*")],
            )
        )

        lambda_function = _lambda.DockerImageFunction(
            self,
            "ETL_lambda_function",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="functions/ETL",
                file="ETL.dockerfile",
            ),
            role=lambda_role,
            environment={"S3_BUCKET": bucket.bucket_name},
        )

        return lambda_function

    def create_outputs(self, bucket, etl_lambda_function):
        CfnOutput(self, "exampleBucketArn", value=bucket.bucket_arn)
        CfnOutput(
            self,
            "lambdaFunctionArn",
            value=etl_lambda_function.function_arn,
        )
