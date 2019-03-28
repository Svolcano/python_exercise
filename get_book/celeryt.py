from celery import Celery

app = Celery('celeryt', broker='amqp://guest@localhost//')


@app.task
def add(x, y):
    return x + y
