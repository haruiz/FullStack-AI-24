FROM python:3.8-slim

# displays logs imidietly to the stream, they wont be part of the buffer
ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY . .

CMD sudo apt-get update
CMD sudo apt-get install postgresql-client

RUN pip install mlflow boto3 google-cloud-storage psycopg2-binary google-cloud-secret-manager click pg8000 wsgi-basic-auth gunicorn python-dotenv

ENTRYPOINT ["/usr/bin/env", "bash", "entrypoint.sh"]

EXPOSE 8080