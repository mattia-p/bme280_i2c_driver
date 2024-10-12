FROM ubuntu:22.04

# Otherwise libsdl2-dev gets stuck at asking geographical region
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
    build-essential

RUN pip3 install Flask
RUN pip3 install plotly
    

# Set working directory
WORKDIR /app

# Copy your source code
COPY . .
