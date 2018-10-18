# Celery Beats SQS Polling Sample
A quick SQS producer/consumer sample where the consumer is driven by Celery beats.

Although this is a total garbage throw-away sample, I am stashing it here for now. :)

## Preparing Workspace
### General
```bash
export PYCURL_SSL_LIBRARY=openssl
python3.6 -m venv --prompt sqs-celery .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Fedora 29
```bash
dnf install curl gcc python3-devel openssl-devel libcurl-devel
```

## Running Locally
Revise the broker and result backend URLs, then:

```bash
docker run --rm -d -p 6379:6379 redis
source .venv/bin/activate
cd consumer && celery -A consumer worker -B -l INFO
python -m producer
```

## Running via Docker
```bash
docker-compose up
source .venv/bin/activate
python -m producer
```