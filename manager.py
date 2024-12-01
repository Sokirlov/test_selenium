import logging

from fastapi import FastAPI
from pydantic import BaseModel
from celery.result import AsyncResult
from pymongo import MongoClient

from settings.config import DB_URL, DB_NAME, DB_COLLECTION
from settings.tasks import scrape_site_task


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(f"[ {__name__} ]")

app = FastAPI()

client = MongoClient(DB_URL)
db = client[DB_NAME]
collection = db[DB_COLLECTION]


class CreateTaskRequest(BaseModel):
    """ Request model for creating a task """
    url: str

@app.post("/", status_code=202)
def create_task(data: CreateTaskRequest):
    """
    When you post url you create task in Celery.
    To view result you need task_id
    """
    url = data.url
    task = scrape_site_task.delay(url)
    logger.info(f'url: {url}, task: {task}')
    return {"task_id": task.id}

@app.get("/{task_id}")
def get_task_status(task_id: str):
    """
    Get status and result of task
    """

    task = AsyncResult(task_id)
    try:
        result = collection.find_one({"taskid": task_id})
        result.pop("_id")
    except Exception as e:
        logger.error(e)
        result = 'Pending data'

    if task.state == "PENDING":
        return {"task_id": task.id, "status": "PENDING", "data": result}
    elif task.state == "SUCCESS":
        return {"task_id": task.id, "status": "SUCCESS", "result": task.result, "data": result}
    elif task.state == "FAILURE":
        return {"task_id": task.id, "status": "FAILURE", "error": str(task.info), "data": result}
    else:
        return {"task_id": task.id, "status": task.state, "data": result}
