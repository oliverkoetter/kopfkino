import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

#redis_url = os.getenv('REDISTOGO_URL')
#redis_url = "redis://:paa343e8d9ef099f17ab77c8fdccc3cfb1a78757c3aee21e13a28426e3acd81d5@ec2-108-128-33-61.eu-west-1.compute.amazonaws.com:29739"
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
#redis_url = (os.environ.get("REDIS_URL"))
print(f"Redis URL geprintet von run-worker.py{redis_url}")
#print(os.getenv("REDISTOGO_URL"))
print(f"set Redis worker instance to {os.getenv('REDISTOGO_URL')}")

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
