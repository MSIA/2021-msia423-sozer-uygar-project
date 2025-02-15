FROM ubuntu:20.04

RUN apt-get update -y && apt-get install -y python3-pip python3-dev git gcc dos2unix g++

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]