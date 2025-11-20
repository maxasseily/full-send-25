FROM python:3.12.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt* ./
RUN if [ -f "requirements.txt" ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    fi

CMD ["bash"]
