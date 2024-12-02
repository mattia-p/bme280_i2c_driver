FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# Update package lists
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    python3 \
    python3-pip \
    i2c-tools \
    cmake \
    sqlite3 \
    g++ \
    build-essential \
    curl \
    vim \
    software-properties-common \
    gnupg \
    libgtest-dev \
    wget \
    apt-transport-https && \
    apt-get clean

RUN pip3 install Flask
RUN pip3 install plotly
RUN pip3 install --no-cache-dir smbus2
RUN pip3 install --no-cache-dir pytz
    
# Set working directory
WORKDIR /app

# Copy your source code
COPY . .
