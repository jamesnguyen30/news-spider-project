from imp import SEARCH_ERROR
from re import I
from jmespath import search
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import logging
import pathlib
import os

from bs4 import BeautifulSoup as bs

CWD = pathlib.Path(__file__).parent.absolute()

class CnnWebdriver():
    def __init__(self):
        self._CNN_URL = 'https://cnn.com'
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        self.chrome_options.add_argument('--ingonito')
        # Turn this on in production to increase execution speed
        # self.chrome_options.headless = True
        self._LOG_DIR = os.path.join(CWD, 'cnn_webdriver_log.txt')
        logging.basicConfig(filename = self._LOG_DIR, level = logging.INFO)

        self.driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()),\
            options=self.chrome_options)
        
        self.driver.set_page_load_timeout(5)

    def stop_driver(self):
        logging.info("Killed driver")
        self.driver.quit()

    def __del__(self):
        self.stop_driver()

    def get_html(self):
        logging.info("Getting html")
        if self.driver.page_source != None:
            logging.error("No html page source! driver didn't access any site yet")
        return self.driver.page_source
    
    def search_by_term(self, term):
        '''
            1. Send the term to searh box and click search button.
            2. Extract links in result list
            3. Scrape all pages
        @params:
            string term: keyword to search
        
        @returns:
            list: list of links to the result
        '''
        search_result_urls = list()
        try:
            SEARCH_URL = '/'.join([self._CNN_URL, 'search'])
            SEARCH_URL += f'?q={term}'

            logging.info("searching url: " + SEARCH_URL)
            self.driver.get(SEARCH_URL)

            h3_search_results = self.driver.find_elements_by_class_name('cnn-search__result-headline') 

            for h3 in h3_search_results:
                href = h3.find_element_by_tag_name('a').get_attribute('href')

                search_result_urls.append(href)

        except Exception as e:
            logging.error(str(e))

        finally:
            return search_result_urls

if __name__ == '__main__':
    cnn_webdriver = CnnWebdriver()
    urls = cnn_webdriver.search_by_term('apple')
    print(urls)
    time.sleep(5)
    cnn_webdriver.stop_driver()




