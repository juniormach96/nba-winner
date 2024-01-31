FROM public.ecr.aws/lambda/python:3.8

# Install build tools
RUN yum update -y && yum install -y \
    gcc-c++ \
    cmake \
    && yum clean all

# Copy and install Python dependencies
COPY requirements-train_ml.txt /var/task/requirements-train_ml.txt
RUN pip install -r requirements-train_ml.txt --no-cache-dir

# Copy your application code
COPY functions/train_ml_model /var/task/

CMD ["train_ml.handler"]
