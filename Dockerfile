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
    g++ \
    build-essential \
    curl \
    software-properties-common \
    gnupg \
    libgtest-dev \
    wget \
    apt-transport-https && \
    apt-get clean

# Install Bazelisk for ARM architecture
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        curl -LO https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64; \
    elif [ "$ARCH" = "aarch64" ]; then \
        curl -LO https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-arm64; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    chmod +x bazelisk-linux-* && \
    mv bazelisk-linux-* /usr/local/bin/bazel

RUN pip3 install Flask
RUN pip3 install plotly
RUN pip3 install --no-cache-dir smbus2
RUN pip3 install --no-cache-dir pytz
    
# Set working directory
WORKDIR /app

# Copy your source code
COPY . .
