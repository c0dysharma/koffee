from fastapi import APIRouter
from celery import uuid
from pydantic import BaseModel
import json

from ..dependencies import review_pr, redis_client, get_job_status_key, get_job_result_key

router = APIRouter()


class PR_details(BaseModel):
    repo_url: str
    pr_number: float
    github_token: str | None = None


@router.post("/analyze-pr/", tags=["reviews"])
async def add_pr_review_task(args: PR_details):
    # a pending task
    job_id = uuid()
    key = get_job_status_key(job_id)
    redis_client.set(key, 'pending')

    # call the LLM to get result
    review_pr.apply_async(
        (job_id, args.repo_url, args.pr_number, args.github_token), task_id=job_id)

    return {'status': 'success', 'job_id': job_id}


@router.get("/status/{job_id}", tags=["reviews"])
def read_status(job_id: str):
    key = get_job_status_key(job_id)

    status = redis_client.get(key)
    return {"job_id": job_id, 'status': status}


@router.get("/results/{job_id}", tags=["reviews"])
async def read_result(job_id: str):
    status_key = get_job_status_key(job_id)
    results_key = get_job_result_key(job_id)

    status = redis_client.get(status_key)
    result = redis_client.get(results_key)
    return {"job_id": job_id, 'status': status, 'results': json.loads(result)}
