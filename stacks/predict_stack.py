from aws_cdk import App, Aws, CfnOutput, Duration, Stack
from aws_cdk import aws_apigateway as apigateway
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

        # Create the Lambda function for the Prediction
        self.predict_lambda_function = self.create_ml_lambda_function(
            s3_bucket=s3_bucket, predict_ecr_repository=predict_ecr_repository
        )
        self.create_api_gateway(self.predict_lambda_function)
        # Outputs
        self.create_outputs(self.predict_lambda_function)

    def create_ml_lambda_function(
        self, s3_bucket: s3.Bucket, predict_ecr_repository: ecr.Repository
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
            "Predict_lambda_function",
            code=_lambda.DockerImageCode.from_image_asset(
                directory=".",
                file="predict.dockerfile",
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
                # resources=[predict_ecr_repository.repository_arn],
                resources=["*"],  # TODO reduce privileges
            )
        )

        return lambda_function

    def create_api_gateway(self, predict_lambda_function):
        # Create a new API Gateway
        api = apigateway.LambdaRestApi(
            self,
            "PredictAPI",
            handler=predict_lambda_function,
            proxy=False,  # Set to False to define individual routes
        )

        # Define a nested resource 'predict/next-games' for GET requests
        predict_resource = api.root.add_resource("predict")
        next_games_resource = predict_resource.add_resource("next-games")
        next_games_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(predict_lambda_function),
        )

        # Output the URL of the API Gateway endpoint
        CfnOutput(
            self,
            "apiEndpoint",
            value=api.url,
            description="URL of the API Gateway endpoint",
        )

    def create_outputs(self, predict_lambda_function):
        CfnOutput(
            self,
            "predictLambdaFunctionArn",
            value=predict_lambda_function.function_arn,
            description="ARN of the ML Predict Lambda Function",
        )
