# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

# Install system dependencies required for Pillow and other libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the application and a dedicated directory for results.
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /app/results && \
    chown -R appuser:appuser /app/results

# Set environment variables
ENV APP_TMP_DATA=/tmp
ENV APP_HOME=/app

WORKDIR ${APP_HOME}

# Copy requirements file from the back folder and install dependencies.
COPY back/requirements.txt .
RUN pip install --upgrade pip && \
python -m pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \ 
pip install -r requirements.txt

# Copy the rest of the application code from the back folder into the container.
# Ownership is set to appuser.
COPY --chown=appuser:appuser back/ ${APP_HOME}

# Make the main executable (api.py) owned by root and non-writable.
USER root
RUN chown root:root ${APP_HOME}/api.py && chmod 555 ${APP_HOME}/api.py

# Switch to the non-root user for running the application.
USER appuser

# Expose port 8000 for the FastAPI application.
EXPOSE 8000

# Set the entrypoint to run the application using "python api.py"
ENTRYPOINT ["python", "api.py"]
