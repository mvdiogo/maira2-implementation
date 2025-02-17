FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

ARG USER_ID
ARG GROUP_ID

RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /app/results && \
    chown -R appuser:appuser /app/results

ENV APP_TMP_DATA=/tmp
ENV APP_HOME=/app

WORKDIR ${APP_HOME}

COPY back/requirements.txt .
RUN pip install --upgrade pip && \
python -m pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \ 
pip install -r requirements.txt

COPY --chown=appuser:appuser back/ ${APP_HOME}

USER root
RUN chown root:root ${APP_HOME}/api.py && chmod 555 ${APP_HOME}/api.py

USER appuser

EXPOSE 8000

ENTRYPOINT ["python", "api.py"]