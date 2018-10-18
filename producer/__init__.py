import json
import time
import boto3

_SQS_QUEUE_NAME = 'sqs-celery-test'
session = boto3.Session(
    aws_access_key_id='public',
    aws_secret_access_key='secret',
    region_name='us-east-1')
sqs = session.resource('sqs')

def get_message(body: str, fifo: bool=False):
    message = {'MessageBody': body}
    if fifo:
        from uuid import uuid4
        message['MessageDeduplicationId'] = str(uuid4())
    return message

def get_body(id: int):
    return json.dumps({'id': id})

messages = map(get_message, map(get_body, range(10)))
queue = sqs.get_queue_by_name(QueueName=_SQS_QUEUE_NAME)
for message in messages:
    response = queue.send_message(**message)
    message_id = response.get('MessageId')
    print(f'sent message (message id: {message_id})')
    time.sleep(1)