FROM python:3.11-slim
WORKDIR /
COPY ./app /app
RUN pip install fastapi uvicorn[standard] sqlalchemy asyncpg pydantic[email] passlib python-jose prometheus_client structlog slowapi python-multipart pytest
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]