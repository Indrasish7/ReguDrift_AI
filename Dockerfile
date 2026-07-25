FROM python:3.12-slim

WORKDIR /app

# Install runtime C++ OpenMP library for FAISS vector engine
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Establish system user accounts for runtime hardening
RUN groupadd -g 10001 regugroup && \
    useradd -u 10001 -g regugroup -m -s /bin/bash reguuser

# Copy codebase elements
COPY --chown=reguuser:regugroup main.py .
COPY --chown=reguuser:regugroup regudrift/ ./regudrift

# Ensure persistent workspace data mounts can be written by reguuser
RUN mkdir -p /app/data && chown -R reguuser:regugroup /app/data

USER reguuser

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
