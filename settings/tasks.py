import logging
from typing import Optional
from celery import Celery, group
from pymongo import MongoClient

from settings.config import BROKER_URL, DB_URL, DB_NAME, DB_COLLECTION
from parsers.parser import WorkUaParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


app = Celery('tasks', broker=BROKER_URL, backend=BROKER_URL)

@app.task(bind=True)
def scrape_site_task(self, url: str, main_data_id: Optional[str] = None):
    """
    Task for fetching data from website
    """
    client = MongoClient(DB_URL)
    db = client[DB_NAME]
    collection = db[DB_COLLECTION]
    logger.info('DB is initialized')

    w = WorkUaParser(request=url)
    logger.info('Parser is initialized')
    pages = w.fetch_search_page()
    logger.info('Page is parsed')

    if not main_data_id:
        logger.info('It`s first page')
        main_data = {
            "taskid": self.request.id,
            "main_url": url,
            "candidates": [],
            "pages": pages
        }
        collection.insert_one(main_data)
        main_data_id = self.request.id
        pages_group_tasks = group(scrape_site_task.s(url=page, main_data_id=main_data_id) for page in pages)
        pages_group_tasks.apply_async()
        logger.info('Task for other {} pages is created'.format(len(pages)))

    new_candidates = w.page_agrigate().get('candidates', [])
    # logger.info('Candidate parsed')
    # c_ = {}
    # for k, v in candidates.items():
    #     c_[f"candidates.{k}"] = v
    # logger.info(f'candidates => {c_}')
    collection.update_one(
        {"taskid": main_data_id},
        {"$push": {"candidates": {"$each": new_candidates}}}
    )
    return {"status": "task_started", "main_data_id": str(main_data_id)}


# if __name__ == '__main__':
#     scrape_site_task(url='https://www.work.ua/resumes-kyiv-python/')