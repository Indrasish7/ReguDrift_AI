# ==========================================
# STAGE 1: Dependency builder stage
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install compilation headers and tools for C++ extensions (e.g., FAISS compile steps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies to user space for clean transfer
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary --user -r requirements.txt


# ==========================================
# STAGE 2: Secure runtime production runner
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Establish system user accounts for runtime hardening (no-root container execution)
RUN groupadd -g 10001 regugroup && \
    useradd -u 10001 -g regugroup -m -s /bin/bash reguuser

# Transfer pre-compiled user packages from Stage 1 builder
COPY --from=builder /root/.local /home/reguuser/.local
ENV PATH=/home/reguuser/.local/bin:$PATH

# Copy codebase elements with strict ownership maps
COPY --chown=reguuser:regugroup main.py .
COPY --chown=reguuser:regugroup regudrift/ ./regudrift

# Ensure persistent workspace data mounts can be written by reguuser
RUN mkdir -p /app/data && chown -R reguuser:regugroup /app/data

# Enable unprivileged application runner
USER reguuser

# Standard FastAPI communication boundaries
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Expose server globally using non-shell CMD specification
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
