FROM python:3.11-slim
WORKDIR /
COPY ./app /app
RUN pip install fastapi uvicorn[standard] sqlalchemy asyncpg grpcio protobuf prometheus_client structlog slowapi pytest
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]