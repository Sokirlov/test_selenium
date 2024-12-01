import abc
import logging
import time

from settings.config import SELENIUM_URL
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from selenium import webdriver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class Driver:
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-dev-shm-usage')  # Optimize for Docker
    options.add_argument('--headless')  # Without graphical interface
    options.add_argument('--no-sandbox')  # Run in sandbox
    options.add_argument('--disable-gpu')

    def chose_proxies(self):
        # TODO Wright mechanic to chose Proxies for each request
        ...

    def __init__(self):
        self.driver = webdriver.Remote(command_executor=SELENIUM_URL, options=self.options)

    def find_elements(self, *args, **kwargs):
        el = self.driver.find_elements(*args, **kwargs)
        return el

    def find_element(self, *args, **kwargs):
        el =self.driver.find_element(*args, **kwargs)
        return el

    def get(self, url):
        try:
            self.driver.get(url)
            time.sleep(1.4)
            return self.driver
        except Exception as e:
            logger.error(e)

    def quit(self):
        if self.driver:
            self.driver.quit()


class BaseParser(abc.ABC):
    data = {}
    urls = []

    @abc.abstractmethod
    def get_last_pagination_page(self, driver) -> int:
        """
        Use driver
        This method must return the number of last page pagination.
        If pagination is not found, return 0.
        """

    @abc.abstractmethod
    def get_candidate_data(self, driver) -> dict:
        """
        Wright code to get data about candidate and build list with objects Candidate
        For page use driver
        :return: Dict with candidate data
        """

    @abc.abstractmethod
    def get_details_urls(self, driver) -> list:
        """
        This method add candidates url, like the detail pages links
        Need get link of candidate CV page an add to detail_pages properties
        Use driver
        :return: list of urls of detail pages or empty list
        """

    @staticmethod
    def get_candidate_id(link) -> str:
        if link.endswith("/"):
            link = link[:-1]
        ids = link.split("/")[-1]
        return ids


    def next_page(self, url: str, page: int) -> str:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params[self.pagination_prefix] = [f"{page}"]
        updated_query = urlencode(query_params, doseq=True)
        updated_url = urlunparse(parsed_url._replace(query=updated_query))
        return str(updated_url)

    def get_pagination(self, last_page) -> list:
        pages = list()
        for i in range(2, last_page, 1):
            link = self.next_page(self.request, i)
            pages.append(link)
        return pages

    def fetch_page(self, url: str) -> None:
        self.driver.get(url=url)
        self.driver.implicitly_wait(1.3)

    def candidate_parse(self):
        self.data['candidates'] = []
        for url in self.urls:
            self.fetch_page(url)
            yield url

    def page_agrigate(self) -> dict:
        logger.info(f'Start parsing candidates')
        for i in self.candidate_parse():
            candidate = {'url': i}
            # candidate_id = self.get_candidate_id(i)
            candidate_data =  self.get_candidate_data(self.driver)
            candidate.update(**candidate_data)
            self.data['candidates'].append(candidate)
        logger.info('Finish this page')
        self.driver.quit()
        return self.data

    def fetch_search_page(self) -> list:
        self.fetch_page(self.request)
        last_pages_ = self.get_last_pagination_page(self.driver)
        pages = self.get_pagination(last_pages_)
        self.data['pages'] = pages
        candidates = self.get_details_urls(self.driver)
        self.urls.extend(candidates)
        logger.info(f'I find {len(candidates)} candidates')
        return pages

    def __init__(self, request: str, pagination_prefix: str = 'page', **kwargs):
        self.request = request
        self.pagination_prefix = pagination_prefix
        self.driver = Driver().driver
