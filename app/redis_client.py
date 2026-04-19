import redis
from rq import Queue

from .config import settings

redis_conn = redis.from_url(settings.redis_url)

email_queue = Queue(
    "emails",
    connection=redis_conn
)