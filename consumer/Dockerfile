FROM python:3.6-alpine
ADD . /opt/service
WORKDIR /opt/service
RUN apk add --no-cache --virtual .build-deps \
    build-base
RUN pip install -r requirements.txt
CMD ["celery", "-A", "consumer", "worker", "-B", "-l", "INFO"]