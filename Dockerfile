
FROM python:2.7

MAINTAINER Dave Kludt

ADD . /anchor
WORKDIR /anchor

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
