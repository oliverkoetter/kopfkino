import os
import celery

print(os.environ.get("TEST_OL_OL"))

app = celery.Celery('example')

url = "redis://:pbf836cf678c990ed74724bdff5cc2ffbaa936980fc6ce1f8cb60daa4e4cf6259@ec2-34-251-167-186.eu-west-1.compute.amazonaws.com:28709"

#app.conf.update(BROKER_URL=os.environ.get['REDIS_URL'],
#                CELERY_RESULT_BACKEND=os.environ.get['REDIS_URL'])

app.conf.update(BROKER_URL=url,
                CELERY_RESULT_BACKEND=url)

@app.task
def add(x, y):
    return x + y


