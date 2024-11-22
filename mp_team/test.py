import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import requests
from bs4 import BeautifulSoup

class eclasscrawling() :
    def __init__(self):
        self.driver = None
        self.class_list = {}
        
    def open_eclass(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.set_page_load_timeout(10)
    
    def login(self):
        self.driver.get("https://ecampus.changwon.ac.kr/login.php")
        time.sleep(0.1) #페이지 로딩 대기
        test_id = "20223126"
        test_passwd = "fullsun0606!"
        
        self.driver.find_element(By.ID,"input-username").send_keys(test_id)
        self.driver.find_element(By.ID,"input-password").send_keys(test_passwd)
        self.driver.find_element(By.NAME,"loginbutton").click()
        time.sleep(0.1)
    
    def open_class(self):
        try:
            ul_element = self.driver.find_element(By.CLASS_NAME, "my-course-lists.coursemos-layout-0")
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")
            
            for i in li_elements:
                class_name = i.find_element(By.CLASS_NAME, "course-title")
                self.class_list[class_name.text] = None
                a_element = i.find_element(By.TAG_NAME, "a")
                a_element.click()  
                WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
                new_window = [window for window in self.driver.window_handles if window != self.driver.current_window_handle][0]
                self.driver.switch_to.window(new_window)
                
                # 페이지 로딩 기다리기
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "add_activities"))
                )
                
                # 과제 찾기
                try:
                    # 과제 요소 기다리기
                    xpath = "//li/a[contains(text(),'과제')]"
                    assignment = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    print("과제 요소가 존재합니다.")
                    assignment.click()  # 과제 클릭
                except NoSuchElementException:
                    print("과제 요소를 찾을 수 없습니다. 창을 닫습니다.")
                    self.driver.close()  # 창 닫기
                    self.driver.switch_to.window(self.driver.window_handles[0])  # 원래 창으로 돌아가기
                    continue  # 다음 for 문으로 넘어감

                except StaleElementReferenceException:
                    print("요소가 더 이상 유효하지 않으므로 다시 시도합니다.")
                    self.driver.close()  # 창 닫기
                    self.driver.switch_to.window(self.driver.window_handles[0])  # 원래 창으로 돌아가기
                    continue  # 다음 for 문으로 넘어감
        except Exception as e:
            print(f"오류 발생: {e}")
        '''
        ul_element = self.driver.find_element(By.CLASS_NAME,"my-course-lists.coursemos-layout-0")
        li_elements = ul_element.find_elements(By.TAG_NAME,"li")
        for i in li_elements:
            class_name = i.find_element(By.CLASS_NAME,"course-title")
            self.class_list[class_name.text] = None
            a_elements = i.find_element(By.TAG_NAME, "a").click()
            time.sleep(0.2)
            activity = self.driver.find_element(By.CLASS_NAME,"add_activities")
            xpath = "//li/a[contains(text(),'과제')]"
            time.sleep(1)
            try:
                assignment = self.driver.find_element(By.XPATH, "//li/a[contains(text(),'과제')]")
                print("과제 요소가 존재합니다.")
                assignment.click
            except NoSuchElementException:
                print("과제 요소를 찾을 수 없습니다. 이전 페이지로 돌아갑니다.")
                self.driver.back()  # 이전 페이지로 돌아가기
            #assignment = self.driver.find_element(By.XPATH,xpath)
            #assignment.click()
            '''
            
            
            
            
            
        
        
if __name__ == "__main__":
    eclass_service = eclasscrawling()
    eclass_service.open_eclass()
    eclass_service.login()
    eclass_service.open_class()
    
    
