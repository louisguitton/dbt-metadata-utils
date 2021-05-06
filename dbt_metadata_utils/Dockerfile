FROM python:3.7-slim

WORKDIR /app

RUN apt-get -y update && \
    apt-get install --no-install-recommends -y \
        git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY dbt_metadata_utils ./dbt_metadata_utils
