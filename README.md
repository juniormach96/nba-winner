
# NBA Winner

This repository contains an AWS CDK (Cloud Development Kit) project designed to automate the extraction, transformation, and loading (ETL) of NBA data, train a machine learning model for predicting NBA game outcomes, and provide predictions through a RESTful API. The system is composed of three main stacks: `ETL`, `train_ml`, and `predict`, each leveraging AWS services for scalable and automated operations.

## Overview

-   **ETL Process**: Extracts NBA data, calculates the moving average of teams' performances, and uploads the processed data to an S3 bucket. This process is containerized in a Docker image, deployed as an AWS Lambda function, and triggered daily by Amazon EventBridge.
    
-   **ML Model Training**: Downloads the processed data from the S3 bucket, trains and optimizes a regression model to predict the points of each team in a match, and uploads the trained model back to the S3 bucket. This stack is also triggered by EventBridge, set to retrain the model monthly.
    
-   **Predict**: Exposes a RESTful API endpoint (`/predict/new-games`) that connects to a Lambda function. This function retrieves the trained model from S3 and uses it to predict outcomes for upcoming NBA matches.
    

## Prerequisites

Before deploying this project, ensure you have the following:

-   AWS CLI installed and configured with appropriate credentials.
-   AWS CDK installed.
-   Python3 installed.
-   Docker installed, for building the ETL process Lambda function.
-   Node.js and npm installed, for managing CDK dependencies.

## Deployment

1.  **Clone the repository**
    
```

git clone https://github.com/juniormach96/nba-winner
cd https://github.com/juniormach96/nba-winner` 

```    
2. **Create a Virtual Environment**

To manually create a virtualenv on MacOS and Linux
```

$ python3 -m venv .venv

```

  

After the init process completes and the virtualenv is created, you can use the following

step to activate your virtualenv.

  

```

$ source .venv/bin/activate

```

  

If you are a Windows platform, you would activate the virtualenv like this:

  

```

% .venv\Scripts\activate.bat

```

  

Once the virtualenv is activated, you can install the required dependencies.

  

```

$ pip install -r requirements.txt

```

  

At this point you can now synthesize the CloudFormation template for this code.

  

```

$ cdk synth

```
    
3.  **Deploy the stacks to your AWS account**
    
    -   Deploy all the stacks:
        
        `cdk deploy --all`
    
3.  **Clean the Resources once you finished**
        
        `cdk destroy`

        

## Usage

-   **ETL Process**: Automatically runs daily. No manual intervention required unless debugging or modifications are needed.
    
-   **ML Model Training**: Automatically retrains every month.
    
-   **Making Predictions**:
    
    -   Send a GET request to the deployed API endpoint `/predict/new-games` to receive predictions for upcoming NBA games.

## Architecture

### SourceStack

The `SourceStack` establishes the infrastructure for source control, Docker image repositories, and data storage, utilizing AWS services:

-   **Amazon S3** Serves as the central repository for storing input and output data, including raw data, processed results, and machine learning models.
-   **AWS CodeCommit** Provides a Git-based repository for the application's code.
-   **Amazon ECR** Hosts Docker images for the ETL process, machine learning training, and prediction service.

### CodeBuildStack

-   **AWS CodeBuild** is configured to trigger builds automatically upon code changes, producing Docker images for the ETL, ML training, and prediction components. It utilizes a `buildspec.yml` file to define build commands and settings.
-   **Integration with AWS Services** includes setting environment variables for AWS account details, ECR repository names, and Lambda function names. This ensures that Docker images are correctly tagged, stored in ECR, and deployed to the respective Lambda functions.

### ETLStack

-   **AWS Lambda **: The ETL process is encapsulated in a Docker container, which is then deployed as a Lambda function. The Docker image is stored in Amazon Elastic Container Registry (ECR), defined on the SourceStack.
-   **Amazon EventBridge**: Scheduled events trigger the ETL Lambda function daily, automating the data processing pipeline without manual intervention.

### TrainMLStack

-   **AWS Lambda **: The ML training process is containerized and deployed as a Lambda function, with the Docker image stored in ECR defined on the SourceStack. 
-   **Amazon EventBridge**: The ML training Lambda function is triggered monthly via EventBridge, and runs every month.

### PredictStack

-   **AWS Lambda & Amazon API Gateway**: The prediction functionality is exposed as a RESTful API through API Gateway, backed by a Lambda function. This Lambda function retrieves the trained ML model from S3 and uses it to predict the outcomes of upcoming NBA matches.
