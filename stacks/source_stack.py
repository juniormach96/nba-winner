from aws_cdk import App, Aws, CfnOutput, Stack
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_s3 as s3


class SourceStack(Stack):
    def __init__(self, scope: App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.s3_bucket = self.create_bucket()
        self.codecommit_repository = self.create_codecommit_repository()
        self.etl_ecr_repository = self.create_ecr_repository(
            repository_name="etl-lambda-repository"
        )
        self.train_ml_ecr_repository = self.create_ecr_repository(
            repository_name="train_ml_ecr_repository"
        )
        self.predict_ecr_repository = self.create_ecr_repository(
            repository_name="predict_ecr_repository"
        )
        self.ecr_repositories = {
            "etl": self.etl_ecr_repository,
            "train_ml": self.train_ml_ecr_repository,
            "predict": self.predict_ecr_repository,
        }

    def create_bucket(self):
        return s3.Bucket(
            self,
            "nba-etl-bucket",
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

    def create_codecommit_repository(self):
        return codecommit.Repository(
            self,
            "NbaEtlRepository",
            repository_name="nba-etl-repository",
            description="Repository for NBA ETL processes",
        )

    def create_ecr_repository(self, repository_name: str):
        return ecr.Repository(self, repository_name, repository_name=repository_name)

    def create_outputs(
        self,
        s3_bucket: s3.Bucket,
    ):
        CfnOutput(
            self,
            "BucketArn",
            value=s3_bucket.bucket_arn,
            description="ARN of the S3 Bucket",
        )
