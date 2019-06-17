FROM python:3.5-alpine

WORKDIR /opt/vision-service/model

COPY . .

RUN apk add --no-cache build-base linux-headers zlib-dev jpeg-dev
RUN pip3 --no-cache-dir install -r requirements.txt

