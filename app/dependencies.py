from celery import Celery
import os
import time
import redis
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
import traceback
from constants import LLM_PROMPT

load_dotenv()

# GEMINI LLM
llm = ChatGoogleGenerativeAI(
    model='gemini-1.5-pro', temperature=0.9, google_api_key=os.getenv('GEMINI_API_KEY'))

# celery configuration
celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
celery_result_backend_url = os.getenv(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery = Celery(__name__)
celery.conf.broker_url = celery_broker_url
celery.conf.result_backend = celery_result_backend_url

# redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")

redis_client = redis.Redis(
    host=redis_host, port=redis_port, decode_responses=True)

# helper functions


def get_job_status_key(job_id: str):
    return f'{job_id}:status'


def get_job_result_key(job_id: str):
    return f'{job_id}:result'


def get_job_error_key(job_id: str):
    return f'{job_id}:error'

# Custom parser


def extract_json(message: str):
    text = message.content
    # Define the regular expression pattern to match JSON blocks
    pattern = r"\`\`\`json(.*?)\`\`\`"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        return [json.loads(match.strip()) for match in matches]
    except Exception:
        print(f"Failed to parse: {message}")
        raise ValueError("Failed to parse data")


def invoke_llm(prompt):
    # Send the prompt to the LLM and return content
    response = llm.invoke(prompt)
    return extract_json(response)


@celery.task(name="review_pr")
def review_pr(job_id: str, repo: str, pr_number: str, github_token: str = None):
    status_key = get_job_status_key(job_id)
    result_key = get_job_result_key(job_id)

    # update status of the task to processing
    redis_client.set(status_key, 'processing')

    try:
        diff_url = f'{repo}/pull/{pr_number}.diff'
        result = invoke_llm(LLM_PROMPT.format(diff=diff_url))

        # if finished successfuly set status and result
        redis_client.set(status_key, 'successful')

        # json to string
        redis_client.set(result_key, json.dumps(result))

    except Exception as e:
        stack_trace = traceback.format_exc()
        redis_client.set(status_key, 'failed')
        redis_client.set(get_job_error_key(job_id), stack_trace)
