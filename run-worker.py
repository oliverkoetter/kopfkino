import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

#redis_url = os.getenv('REDISTOGO_URL')
redis_url = "redis://redistogo:3f1232c25d4635ab5422d0cced370d16@soapfish.redistogo.com:10834/"
print(os.getenv("REDISTOGO_URL"))
print(f"set Redis worker instance to {os.getenv('REDISTOGO_URL')}")

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()