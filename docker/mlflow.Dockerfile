FROM python:3.11-slim

WORKDIR /mlflow

RUN pip install --no-cache-dir mlflow==2.9.2

RUN mkdir -p /mlflow/artifacts /mlflow/db

EXPOSE 5000

CMD ["mlflow", "server", \
     "--backend-store-uri", "sqlite:///mlflow/db/mlflow.db", \
     "--default-artifact-root", "/mlflow/artifacts", \
     "--host", "0.0.0.0", \
     "--port", "5000"]
