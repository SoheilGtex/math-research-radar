# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

# Set environment variables to optimize Python runtime during build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install OS-level build dependencies (required for compiling certain Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create a self-contained virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory for the build process
WORKDIR /build

# Upgrade build tools
RUN pip install --upgrade pip wheel

# Copy package definitions and source code
COPY pyproject.toml .
COPY src/ src/

# Install the application into the virtual environment
RUN pip install .

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.12-slim

# Set environment variables for the runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Create a non-root user and group for security
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

# Set the working directory
WORKDIR /app

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy only the necessary runtime files
COPY src/ src/
COPY main.py .

# Create necessary directories for local storage mapping and assign ownership
RUN mkdir -p papers stats docs cache logs && \
    chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Define the entrypoint command to run the pipeline
CMD ["python", "main.py"]