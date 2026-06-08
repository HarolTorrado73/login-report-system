# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

COPY --from=builder /install /usr/local
COPY migrations/ ./migrations/
COPY app/ ./app/
COPY data/ ./data/
COPY run.py .

USER appuser

EXPOSE 5000

ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--timeout", "120", "--workers", "2", "run:app"]
