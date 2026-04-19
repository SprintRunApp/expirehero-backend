import redis
from rq import Worker, Queue, Connection

from app.config import settings

from jinja2 import Template

redis_conn = redis.from_url(settings.redis_url)

with Connection(redis_conn):

    worker = Worker([Queue("emails")])

    worker.work()