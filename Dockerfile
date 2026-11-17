
# Stage 1: Install Python dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install --no-cache-dir \
        --upgrade pip setuptools wheel && \
    /opt/venv/bin/python -m pip install --no-cache-dir \
        -r requirements.txt && \
    /opt/venv/bin/python -m pip check && \
    /opt/venv/bin/python -m pip uninstall -y pip setuptools wheel

# Stage 2: Production runtime
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
RUN rm -rf /usr/local/lib/python3.11/site-packages/setuptools \
    /usr/local/lib/python3.11/site-packages/setuptools-*.dist-info \
    /usr/local/lib/python3.11/site-packages/wheel \
    /usr/local/lib/python3.11/site-packages/wheel-*.dist-info

COPY . .

RUN groupadd --system appgroup && \
    useradd --system --gid appgroup appuser && \
    chown -R appuser:appgroup /app /opt/venv

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s \
    --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
