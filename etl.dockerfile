FROM public.ecr.aws/lambda/python:3.8

COPY requirements-etl.txt /var/task/requirements-etl.txt

RUN pip install -r requirements-etl.txt

COPY functions/ETL /var/task/

CMD ["etl.handler"]
