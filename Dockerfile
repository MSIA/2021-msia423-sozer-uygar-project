FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y python3-pip python3-dev git gcc g++

WORKDIR /ingest

COPY ./requirements.txt /ingest/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /ingest

ENTRYPOINT [ "python3" ]