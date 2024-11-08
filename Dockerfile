# Use Python 3.13.0-slim as the base image
FROM python:3.13.0-slim

# Define APT packages to install (compilers, development libraries, etc.)
ENV APT_PACKAGES="gcc g++ libffi-dev libssl-dev libxslt-dev python3-dev"

# Set the working directory in the container
WORKDIR /code

# Add requirements.txt for pip dependency management
ADD requirements.txt requirements.txt

# Install system dependencies and Python dependencies, then clean up
RUN apt-get update && \
    apt-get install -y ${APT_PACKAGES} && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get purge -y ${APT_PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

# Add the Scrapy configuration file and the project directory
ADD scrapy.cfg scrapy.cfg
ADD raspadorlegislativo /code/raspadorlegislativo