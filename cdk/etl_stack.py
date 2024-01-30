from aws_cdk import App, Aws, CfnOutput, Duration, Stack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3


class ETLStack(Stack):
    def __init__(
        self,
        app: App,
        id: str,
        s3_bucket: s3.Bucket,
        etl_ecr_repository: ecr.Repository,
    ) -> None:
        super().__init__(app, id)

        self.etl_lambda_function = self.create_etl_lambda_function(
            s3_bucket=s3_bucket, ecr_repository=etl_ecr_repository
        )
        self.create_outputs(self.etl_lambda_function)

    def create_etl_lambda_function(
        self, s3_bucket: s3.Bucket, ecr_repository: ecr.Repository
    ):
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[s3_bucket.bucket_arn, s3_bucket.arn_for_objects("*")],
            )
        )
        # Grant ECR pull permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ecr:*"],
                resources=[ecr_repository.repository_arn],
            )
        )

        lambda_function = _lambda.DockerImageFunction(
            self,
            "ETL_lambda_function",
            code=_lambda.DockerImageCode.from_image_asset(
                directory=".",
                file="etl.dockerfile",
            ),
            role=lambda_role,
            environment={"S3_BUCKET": s3_bucket.bucket_name},
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        return lambda_function

    def create_outputs(self, etl_lambda_function: _lambda.Function):
        CfnOutput(
            self,
            "lambdaFunctionArn",
            value=etl_lambda_function.function_arn,
            description="ARN of the ETL Lambda Function",
        )
