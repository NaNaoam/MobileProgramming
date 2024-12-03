import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import TimeoutException
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
 
        ul_element = self.driver.find_element(By.CLASS_NAME, "my-course-lists.coursemos-layout-0")
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        for i in li_elements:
        
            # 클래스 이름 가져오기
            class_name = i.find_element(By.CLASS_NAME, "course-title")
            self.class_list[class_name.text] = None
            a_element = i.find_element(By.TAG_NAME, "a")
            href = a_element.get_attribute('href')
            self.driver.execute_script("window.open(arguments[0]);", href)
            new_window = self.driver.window_handles[-1]  # 마지막 창을 선택
            # 새 창이 열릴 때까지 대기 (최대 10초)
            self.driver.switch_to.window(new_window)  # 새 창으로 전환
            xpath = "//li/a[contains(text(),'과제')]"
            assignment_elements = self.driver.find_elements(By.XPATH, xpath)
        
            if assignment_elements:  
                time.sleep(1)
                assignment = assignment_elements[0]  
                div_element = self.driver.find_element(By.CLASS_NAME, "block.block-coursemos.block-quick-mod")
                li_element_2 = div_element.find_element(By.TAG_NAME,"li")
                a_element_2 = li_element_2.find_element(By.TAG_NAME, "a")
                href_ar = a_element_2.get_attribute('href')
                ###이후 수정
                print(href_ar)
                print("E2")
                self.driver.execute_script("window.open(arguments[0]);", href_ar)
                print("E3")
                new_window_ = self.driver.window_handles[-1]
                self.driver.switch_to.window(new_window_)
                time.sleep(1)
                
                tbody_elements = self.driver.find_elements(By.TAG_NAME, "tbody")
                text_ = tbody_elements.find_element(By.CLASS_NAME, "cell c1")
                print(text_.text())
                
                
                
            else:  
                time.sleep(1)
                print("과제 요소를 찾을 수 없습니다.")
                print("3")
                self.driver.close()  
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(1)
            continue  
    

            
            '''           
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
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.back() 
            time.sleep(1)
            print(f"오류 발생: {e}")
     
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
    
    
