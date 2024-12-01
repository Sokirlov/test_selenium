import logging

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from .base import BaseParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class WorkUaParser(BaseParser):
    """
    This class parser for  work ua site.
    Each new parser base on BaseParser and mast have own methods:
    - get_last_pagination_page: return int of last page.
        If pages build with url params you can set name of params.
        By default, used params page.

    - get_details_urls: return list with urls of candidates or empty list

    - get_candidate_data: return dict with candidate date

    """

    def executor_find(self, *args) -> str:
        try:
            data = self.driver.find_element(*args)
            if data:
                data = data.text
        except NoSuchElementException:
            data = ""
        return data

    def get_skills(self) -> list:
        skills = []
        try:
            all_skills = self.driver.find_elements(By.CLASS_NAME, 'label-skill')
            # skills_ = all_skills.find_elements(By.TAG_NAME, 'li')
            for i in all_skills:
                skills.append(i.text)
        except NoSuchElementException:
            ...
        return skills

    def get_candidate_data(self, driver) -> dict:
        candidate = {
            "name": self.executor_find(By.TAG_NAME, "h1"),
            "position": self.executor_find(By.TAG_NAME, "h2"),
            "skill": self.get_skills(),
            # "raw_page": driver.page_source,
        }
        return candidate

    def get_details_urls(self, driver) -> list:
        urls = []
        candidates = self.driver.find_elements(By.TAG_NAME, "h2")
        for candidate in candidates:
            try:
                link = candidate.find_element(By.TAG_NAME, "a")
                if link is not None:
                    link = link.get_attribute("href")
            except Exception as e:
                # logger.error(e)
                continue
            urls.append(link)
        return urls

    def get_last_pagination_page(self, driver) -> int:
        last_page = 0
        try:
            pagination = driver.find_element(By.CLASS_NAME, "pagination")
        except NoSuchElementException:
            return last_page

        page_links = pagination.find_elements(By.TAG_NAME, "a")
        for link in page_links:
            href = link.get_attribute("href")
            if href and "page=" in href:
                page_number = int(href.split("page=")[-1])
                last_page = max(last_page, page_number)
        return last_page


    def __init__(self, request, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
