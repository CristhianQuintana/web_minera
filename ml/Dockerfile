FROM python:3.11-slim
WORKDIR /app

COPY requirements.hashed.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY __init__.py .
COPY adapters adapters
COPY application application
COPY composition composition
COPY domain domain
COPY ports ports
COPY presentation presentation

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "adapters.inbound.http.main:app", "--host", "0.0.0.0", "--port", "8001"]
