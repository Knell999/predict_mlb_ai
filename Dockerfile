# Stage 1: Builder - 의존성 설치
FROM python:3.11-slim AS builder

WORKDIR /app

# Install UV package manager
RUN pip install --no-cache-dir uv

# Copy dependency files (README.md needed by hatchling build)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using UV (frozen lock file)
RUN uv sync --frozen

# Stage 2: Runtime - 애플리케이션 실행
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY *.py ./
COPY data/ ./data/
COPY font/ ./font/
COPY *.png *.jpg ./

# Create logs directory
RUN mkdir -p logs

# Create non-root user for security
RUN useradd -m -u 1000 mlbuser && \
    chown -R mlbuser:mlbuser /app

USER mlbuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
