FROM python:3.9-alpine

WORKDIR /usr/src/app

RUN apk add build-base

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK CMD discordhealthcheck || exit 1

CMD [ "python", "./main.py" ]