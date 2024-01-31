FROM public.ecr.aws/lambda/python:3.8

# Copy and install Python dependencies
COPY requirements-predict.txt /var/task/requirements-predict.txt
RUN pip install -r requirements-predict.txt --no-cache-dir

# Copy your application code
COPY functions/predict /var/task/

CMD ["predict.handler"]
