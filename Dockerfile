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
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirement files if present
COPY requirements*.txt ./
RUN if ls requirements*.txt >/dev/null 2>&1; then \
      pip wheel --wheel-dir /wheels -r requirements.txt; \
    else echo "No requirements.txt found, skipping dependency wheel build"; fi

############################
# Runtime stage
############################
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PORT=8080

WORKDIR /app

# Apply Aliyun mirrors again in runtime image (builder layers not shared)
RUN set -eux; \
    . /etc/os-release; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${VERSION_CODENAME} main contrib non-free non-free-firmware" > /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${VERSION_CODENAME}-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${VERSION_CODENAME}-backports main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security ${VERSION_CODENAME}-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    apt-get update && apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r app && useradd -r -g app app

# Copy built wheels & install
COPY --from=builder /wheels /wheels
RUN if [ -d /wheels ]; then pip install --no-cache-dir /wheels/*; fi

# Copy source code
COPY . .

# Fix ownership
RUN chown -R app:app /app
USER app

EXPOSE 8000

# Healthcheck expects the app to expose /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,os,sys; \
    url=f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8000\")}/health'; \
    urllib.request.urlopen(url).read()" || exit 1

# Entrypoint (adjust module/package if different)
# If your server starts with `python -m mcp_servers`, this works; override CMD for alt modes.
ENTRYPOINT ["python", "main.py"]
#CMD ["serve"]


