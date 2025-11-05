# Multi-stage Dockerfile for security MCP server

############################
# Builder stage
############################
FROM artifact.roche.com.cn/common-dockerhub-docker-r/python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Use Aliyun Debian mirrors for faster apt operations
RUN set -eux; \
    . /etc/os-release; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${VERSION_CODENAME} main contrib non-free non-free-firmware" > /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${VERSION_CODENAME}-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${VERSION_CODENAME}-backports main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security ${VERSION_CODENAME}-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    apt-get update && \
    apt-get install -y --no-install-recommends build-essential python3-dev curl && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Copy requirement files if present
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN if [ -f requirements.txt ]; then pip wheel -vv --wheel-dir /wheels -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple; fi

############################
# Runtime stage
############################
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_HOME=/app PORT=8000
WORKDIR /app
RUN set -eux; \
    . /etc/os-release; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${VERSION_CODENAME} main contrib non-free non-free-firmware" > /etc/apt/sources.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl; \
    apt-get clean; rm -rf /var/lib/apt/lists*
RUN groupadd -r app && useradd -r -g app app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY . .
RUN chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8000\")}/health').read()" || exit 1
ENTRYPOINT ["python","main.py"]


