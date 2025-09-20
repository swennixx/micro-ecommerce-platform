FROM python:3.11-slim
WORKDIR /app
COPY ./app /app
RUN pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary grpcio grpcio-tools
# Запускать оба сервера: HTTP (FastAPI) и gRPC
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & python grpc_server.py"]