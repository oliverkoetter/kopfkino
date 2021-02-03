import os
import urllib.parse
from redis import Redis
from rq import Queue, Connection
from rq.worker import HerokuWorker as Worker

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL')
if not redis_url:
    raise RuntimeError('Set up Redis To Go first.')

urllib.parse.uses_netloc.append('redis')
url = urllib.parse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
