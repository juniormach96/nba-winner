# Start from the official Ubuntu base image
FROM ubuntu:latest

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common less curl

# Add the repository for the latest Node.js LTS version
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -

# Install Node.js and Python
RUN apt-get install -y nodejs python3 python3-pip

# Install AWS CLI and AWS CDK
RUN pip install awscli awscli-local && \
    npm install -g aws-cdk aws-cdk-local

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN cdk synth

CMD ["tail", "-f", "/dev/null"]
# RUN cdk deploy
# Set the default command for the container