from celery import Celery
import os
import time
import redis

celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
celery_result_backend_url = os.getenv(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery = Celery(__name__)
celery.conf.broker_url = celery_broker_url
celery.conf.result_backend = celery_result_backend_url


redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")

redis_client = redis.Redis(
    host=redis_host, port=redis_port, decode_responses=True)


def get_job_status_key(job_id: str):
    return f'{job_id}:status'


def get_job_result_key(job_id: str):
    return f'{job_id}:result'


@celery.task(name="review_pr")
def review_pr(job_id: str, repo: str, pr_number: str, github_token: str = None):
    key = get_job_status_key(job_id)
    redis_client.set(key, 'processing')
    print(job_id, repo, pr_number, github_token)

    time.sleep(30)

    redis_client.set(key, 'successful')
