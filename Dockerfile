# syntax=docker/dockerfile:1

# Stage 1: Build webapp
FROM node:18-slim AS webapp-builder

WORKDIR /build/webapp
COPY webapp/ .
RUN npm install && npm run build

# Stage 2: Build blrec image
FROM python:3.11-slim-bookworm

ARG USE_MIRRORS=false
ARG APT_MIRROR=mirrors.tuna.tsinghua.edu.cn
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple

WORKDIR /app
VOLUME ["/cfg", "/log", "/rec"]

# Copy webapp build output (angular.json outputs to ../src/blrec/data/webapp/)
COPY --from=webapp-builder /build/src/blrec/data/webapp/ src/blrec/data/webapp/

# Copy source and project config
COPY pyproject.toml README.md ./
COPY src/ src/

# Install system dependencies and Python package
RUN if [ "$USE_MIRRORS" = "true" ]; then \
      if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i "s|deb.debian.org|${APT_MIRROR}|g" /etc/apt/sources.list.d/debian.sources; \
      else \
        sed -i "s|deb.debian.org|${APT_MIRROR}|g" /etc/apt/sources.list && \
        sed -i "s|security.debian.org|${APT_MIRROR}|g" /etc/apt/sources.list; \
      fi; \
    fi && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    if [ "$USE_MIRRORS" = "true" ]; then \
      pip install --no-cache-dir -i "$PIP_INDEX_URL" -e .; \
    else \
      pip install --no-cache-dir -e .; \
    fi && \
    apt-get purge -y --auto-remove build-essential python3-dev

ENV BLREC_DEFAULT_SETTINGS_FILE=/cfg/settings.toml
ENV BLREC_DEFAULT_LOG_DIR=/log
ENV BLREC_DEFAULT_OUT_DIR=/rec
ENV TZ="Asia/Shanghai"

EXPOSE 2233
ENTRYPOINT ["blrec", "--host", "0.0.0.0", "--no-progress"]
CMD []
