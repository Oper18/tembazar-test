FROM python:3.9.16

WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN apt update \
  && pip install --upgrade pip \
  && pip install -U pip setuptools \
  && pip install -r requirements.txt
COPY ./ ./
