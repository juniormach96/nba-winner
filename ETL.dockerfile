FROM public.ecr.aws/lambda/python:3.8

COPY requirements-etl.txt requirements-etl.txt

RUN pip install -r requirements-etl.txt

COPY . .

CMD ["etl.handler"]
