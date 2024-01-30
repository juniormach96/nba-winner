class TrainMLStack(Stack):
    def __init__(self, app: App, id: str, bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # Create the Lambda function for the ML training
        ml_lambda_function = self.create_ml_lambda_function(bucket)

        # Outputs
        self.create_outputs(ml_lambda_function)

    def create_ml_lambda_function(self, bucket):
        ml_lambda_role = iam.Role(
            self,
            "MLLambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        # Grant necessary permissions to the Lambda role
        ml_lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[bucket.bucket_arn, bucket.arn_for_objects("*")],
            )
        )

        ml_lambda_function = _lambda.DockerImageFunction(
            self,
            "MLTrain_lambda_function",
            code=_lambda.DockerImageCode.from_image_asset(
                directory=".",
                file="train_ml.dockerfile",  # Dockerfile for ML training
            ),
            role=ml_lambda_role,
            environment={"S3_BUCKET": bucket.bucket_name},
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        return ml_lambda_function

    def create_outputs(self, ml_lambda_function):
        CfnOutput(
            self,
            "mlLambdaFunctionArn",
            value=ml_lambda_function.function_arn,
            description="ARN of the ML Training Lambda Function",
        )
