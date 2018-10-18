from celery import Celery, chain
from celery.utils.log import get_task_logger
from consumer import configuration
import boto3

app = Celery('tasks', config_source=configuration)
logger = get_task_logger(__name__)

_SQS_QUEUE_NAME = 'sqs-celery-test'
session = boto3.Session(
    aws_access_key_id='public',
    aws_secret_access_key='secret',
    region_name='us-east-1')
sqs = session.resource('sqs')


@app.on_after_configure.connect
def add_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, consume_sqs_queue.s(_SQS_QUEUE_NAME), name='consume sqs queue')


_MESSAGE_BUNDLE_SIZE = 3
_MESSAGE_BUNDLE_TIMEOUT_SECONDS = 3
@app.task(ignore_result=True)
def consume_sqs_queue(queue_name: str):
    import time
    import json

    queue = sqs.get_queue_by_name(QueueName=queue_name)
    messages = []

    start_time = time.monotonic()
    while len(messages) < _MESSAGE_BUNDLE_SIZE:
        messages.extend(queue.receive_messages(WaitTimeSeconds=3))
        if time.monotonic() - start_time > _MESSAGE_BUNDLE_TIMEOUT_SECONDS:
            break
    logger.info('processing %s messages from sqs queue: %s', len(messages), queue_name)
    for message in messages:
        m_id = message.message_id
        m_body = json.loads(message.body)
        logger.info('processing message; mid: %s: %s', m_id, m_body)
        chain = (compute_hash.s(body=m_body)
               | store_hash.s(body=m_body)
               | resolve_message.s(id=m_id, queue_name=queue_name, receipt_handle=message.receipt_handle))
        chain()


@app.task
def compute_hash(body: dict):
    import hashlib
    import time
    time.sleep(5)
    b_hash = hashlib.sha256(str(body['id']).encode()).hexdigest()[:4]
    logger.info('compute hash; id: %s = %s', body['id'], b_hash)
    return b_hash


@app.task
def store_hash(hash_result: tuple, body: dict):
    import random
    success = random.randint(1, 10) > 3
    if success:
        logger.info('stored hash; id: %s = %s', body['id'], hash_result)
    else:
        logger.error('failed to store hash: id: %s = %s', body['id'], hash_result)
    return success


@app.task(ignore_result=True)
def resolve_message(success: bool, id: str, queue_name: str, receipt_handle: str):
    if success:
        logger.info('deleting message; mid: %s', id)
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        queue.delete_messages(Entries=[{ 'Id': '1', 'ReceiptHandle': receipt_handle }])
    else:
        logger.error('failed message; mid: %s', id)


if __name__ == '__main__':
    app.start()