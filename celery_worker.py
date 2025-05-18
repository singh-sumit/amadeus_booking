from celery import Celery
import os

from core import config

celery = Celery(
    "worker",
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE,  # or CERT_OPTIONAL / CERT_REQUIRED as needed
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE,  # adjust for production
    }
)

# celery = Celery(
#     "worker",
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/1",  # ✅ Add this
# )

celery.conf.update(
    task_track_started=True,
    result_expires=3600,
)


# Import tasks module here to register tasks
import worker.tasks  # <-- THIS IS IMPORTANT