from aws_cdk import App, Aws, CfnOutput, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3


class S3ObjectLambdaStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        self.bucket = self.create_bucket()
        self.etl_lambda_function = self.create_etl_lambda_function(self.bucket)
        self.create_outputs()

    def create_bucket(self):
        bucket = s3.Bucket(
            self,
            "example-bucket",
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

        lambda_function = _lambda.Function(
            self,
            "ETL_lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="main.handler",
            code=_lambda.Code.from_asset("functions/ETL"),
            role=lambda_role,
        )
        return lambda_function

    def create_outputs(self):
        CfnOutput(self, "exampleBucketArn", value=self.bucket.bucket_arn)
        CfnOutput(
            self,
            "lambdaFunctionArn",
            value=self.etl_lambda_function.function_arn,
        )
