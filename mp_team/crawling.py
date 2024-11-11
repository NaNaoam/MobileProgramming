import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import requests
from bs4 import BeautifulSoup

class eclasscrawling() :
    def __init__(self):
        self.driver = None
        
    def open_eclass(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.set_page_load_timeout(10)
    
    def login(self):
        self.driver.get("https://ecampus.changwon.ac.kr/login.php")
        time.sleep(2) #페이지 로딩 대기
        test_id = "20223126"
        test_passwd = "fullsun0606!"
        
        self.driver.find_element(By.ID,"input-username").send_keys(test_id)
        self.driver.find_element(By.ID,"input-password").send_keys(test_passwd)
        self.driver.find_element(By.NAME,"loginbutton").click()
        time.sleep(2)
    
    def open_calendar(self):
        self.driver.get("https://ecampus.changwon.ac.kr/calendar/view.php?view=month&cal_m=11")
        time.sleep(2)
        
    
if __name__ == "__main__":
    eclass_service = eclasscrawling()
    eclass_service.open_eclass()
    eclass_service.login()
    eclass_service.open_calendar()
    
    
