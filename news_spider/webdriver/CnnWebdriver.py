from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class CnnWebdriver():
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        self.chrome_options.add_argument('--ingonito')
        # Turn this on in production to increase execution speed
        # self.chrome_options.headless = True

        self.driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()),\
            chrome_options=self.chrome_options)
    def stop_driver(self):
        self.driver.quit()

    def __del__(self):
        self.stop_driver()
    
    def search_by_term(self, term):
        '''
            Send the term to searh box and click search button
        '''
