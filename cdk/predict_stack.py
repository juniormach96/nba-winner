from aws_cdk import App, Aws, CfnOutput, Duration, Stack
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3


class PredictStack(Stack):
    def __init__(
        self,
        app: App,
        id: str,
        s3_bucket: s3.Bucket,
        predict_ecr_repository: ecr.Repository,
        **kwargs
    ) -> None:
        super().__init__(app, id, **kwargs)

        # Create the Lambda function for the ML training
        self.train_ml_lambda_function = self.create_ml_lambda_function(
            s3_bucket=s3_bucket, train_ml_ecr_repository=train_ml_ecr_repository
        )
        # Outputs
        self.create_outputs(self.train_ml_lambda_function)

    def create_ml_lambda_function(
        self, s3_bucket: s3.Bucket, train_ml_ecr_repository: ecr.Repository
    ):
        lambda_role = iam.Role(
            self,
            "MLLambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        # Grant necessary permissions to the Lambda role
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[s3_bucket.bucket_arn, s3_bucket.arn_for_objects("*")],
            )
        )

        lambda_function = _lambda.DockerImageFunction(
            self,
            "TrainML_lambda_function",
            code=_lambda.DockerImageCode.from_image_asset(
                directory=".",
                file="train_ml.dockerfile",
            ),
            role=lambda_role,
            environment={
                "S3_BUCKET": s3_bucket.bucket_name,
                "TRAIN_FILE_NAME": "to_predict.csv",
                "ML_MODEL_FILE": "best_model.pkl",
            },
            memory_size=3008,
            timeout=Duration.minutes(10),
        )

        # Grant ECR pull permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ecr:*"],
                resources=[train_ml_ecr_repository.repository_arn],
            )
        )

        return lambda_function

    def create_outputs(self, ml_lambda_function):
        CfnOutput(
            self,
            "mlLambdaFunctionArn",
            value=ml_lambda_function.function_arn,
            description="ARN of the ML Training Lambda Function",
        )