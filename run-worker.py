'''
import os
from urllib.parse import urlparse
from redis import Redis
from rq import Queue, Connection
from rq.worker import HerokuWorker as Worker

listen = ['high', 'default', 'low']

#redis_url = os.getenv('REDISTOGO_URL')
redis_url = "redis://redistogo:3f1232c25d4635ab5422d0cced370d16@soapfish.redistogo.com:10834/"
if not redis_url:
    raise RuntimeError('Set up Redis To Go first.')

urllib.parse.urlparse.uses_netloc.append('redis')
url = urllib.parse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

print(f"Meldung aus run-worker.py: {os.getenv('FLASK_ENV')}")
print(f"Meldung aus run-worker.py: {os.getenv('REDISTOGO_URL')}")

'''

import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

#redis_url = os.getenv('REDISTOGO_URL')
redis_url = "redis://redistogo:6bb2c081c8cd8ab5b45b745044da3a7f@soapfish.redistogo.com:9322/"
print(os.getenv("REDISTOGO_URL"))
print(f"set Redis worker instance to {os.getenv('REDISTOGO_URL')}")

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
