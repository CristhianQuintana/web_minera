FROM python:3.11-slim
WORKDIR /app

COPY requirements.lock.txt .
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.lock.txt

COPY __init__.py .
COPY adapters adapters
COPY application application
COPY composition composition
COPY domain domain
COPY ports ports
COPY presentation presentation

ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "adapters.inbound.http.main:app", "--host", "0.0.0.0", "--port", "8001"]
