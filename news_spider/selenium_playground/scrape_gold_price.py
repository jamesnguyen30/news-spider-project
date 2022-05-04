#tutorial: https://medium.com/codex/web-scraping-paginated-webpages-with-python-selenium-and-beautifulsoup4-8b415f833132
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup as bs

class G2G_Scraper():
    def __init__(self):

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        self.driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()),\
            chrome_options=self.chrome_options)
        self.driver.set_page_load_timeout(5)
        
    def get_server_links(self):
        url = 'https://www.g2g.com/categories/lost-ark-gold'
        # url = 'https://www.g2g.com/categories/lost-ark-gold?page=2'

        self.driver.get(url)

        time.sleep(5)
        html = self.driver.page_source

        with open("g2g.html", 'w', encoding='utf-8') as file:
            print("writing html")
            file.write(html)

        soup = bs(html, features = 'html.parser')

        boxes = soup.find_all('div', class_ = 'col-12 col-md-3')
        links = list()
        for box in boxes:
            links.append(box.find('a', href = True)['href'])

        return links

    def check_exists(self,xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException as e:
            return False
        finally:
            return True
    
    def click_page(self):
        try:
            is_next_button_clickable = WebDriverWait(self.driver, 5).until(
                ec.element_to_be_clickable((By.XPATH, '//*[@id="q-app"]/div/div[1]/div[1]/div[5]/div/div[2]/div[3]/div/button[2]'))
            ) 
            next_button = self.driver.find_element(By.XPATH, '//*[@id="q-app"]/div/div[1]/div[1]/div[5]/div/div[2]/div[3]/div/button[2]')
            # self.driver.execute_script('arguments[0].scrollIntoView();', next_button)
            # self.driver.execute_script('window.scrollBy(0, -200);')
            # ActionChains(self.driver).move_to_element(next_button).click().perform()
            self.driver.execute_script('arguments[0].click()', next_button)
            time.sleep(2)
            # next_button.click()
            print('clicked next button')
        except Exception as e:
            print(e)
            print('not clickable')

    def stop_driver(self):
        self.driver.quit()
    
    def __del__(self):
        self.stop_driver()

if __name__=='__main__':
    scraper = G2G_Scraper()

    links = scraper.get_server_links()

    # print(links)

    scraper.click_page()

    print("Done executtion")
    time.sleep(5)

    scraper.stop_driver()
    # scraper.run()

