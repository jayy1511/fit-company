FROM python:3.12-slim

WORKDIR /app

COPY ./src/stats /app

RUN pip install --no-cache-dir flask flask_sqlalchemy psycopg2-binary pika pymongo

ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=5003
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH=/app

CMD ["flask", "run"]
