FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install requests

ENTRYPOINT ["python", "/app/main.py"]
