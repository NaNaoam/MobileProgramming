from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time
from DB_save import AssignmentDatabase

class EclassCrawler:
    def __init__(self, studno):
        self.driver = None
        self.class_list = {}
        self.studno = studno

    def open_eclass(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.set_page_load_timeout(20)  # 타임아웃도 20초로 증가

    def login(self, user_id, password):
        self.driver.get("https://ecampus.changwon.ac.kr/login.php")
        WebDriverWait(self.driver, 15).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )

        self.driver.find_element(By.ID, "input-username").send_keys(user_id)
        self.driver.find_element(By.ID, "input-password").send_keys(password)
        self.driver.find_element(By.NAME, "loginbutton").click()

        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )

        if "login" not in self.driver.current_url:
            return True
        else:
            return False

    
    def open_class(self):
        assignments = []
        try:
            ul_element = self.driver.find_element(By.CLASS_NAME, "my-course-lists.coursemos-layout-0")
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")

            for i in li_elements:
                try:
                    class_findname = i.find_element(By.CLASS_NAME, "course-title")
                    class_name = class_findname.find_element(By.TAG_NAME, "h3").text
                    print(f"과목명: {class_name} 처리 시작")

                    a_element = i.find_element(By.TAG_NAME, "a")
                    href = a_element.get_attribute('href')
                    self.driver.execute_script("window.open(arguments[0]);", href)
                    new_window = self.driver.window_handles[-1]
                    self.driver.switch_to.window(new_window)

                    WebDriverWait(self.driver, 20).until(
                        lambda driver: driver.execute_script('return document.readyState') == 'complete'
                    )

                    xpath = "//li/a[contains(text(),'과제')]"
                    assignment_elements = self.driver.find_elements(By.XPATH, xpath)

                    if assignment_elements:
                        WebDriverWait(self.driver, 20).until(
                            lambda driver: driver.execute_script('return document.readyState') == 'complete'
                        )

                        try:
                            div_element = WebDriverWait(self.driver, 10).until(
                                lambda x: x.find_element(By.CLASS_NAME, "block.block-coursemos.block-quick-mod")
                            )
                            li_element_2 = div_element.find_element(By.TAG_NAME, "li")
                            a_element_2 = li_element_2.find_element(By.TAG_NAME, "a")
                            href_ar = a_element_2.get_attribute('href')

                            self.driver.execute_script("window.open(arguments[0]);", href_ar)
                            new_window_ = self.driver.window_handles[-1]
                            self.driver.switch_to.window(new_window_)

                            WebDriverWait(self.driver, 20).until(
                                lambda driver: driver.execute_script('return document.readyState') == 'complete'
                            )

                            tbody_elements = WebDriverWait(self.driver, 10).until(
                                lambda x: x.find_element(By.TAG_NAME, "tbody")
                            )
                            tr_elements = tbody_elements.find_elements(By.TAG_NAME, "tr")

                            for tr in tr_elements:
                                try:
                                    td_elements = tr.find_elements(By.TAG_NAME, "td")
                                    if len(td_elements) > 3:
                                        assignment = tr.find_element(By.CLASS_NAME, "cell.c1")
                                        find_url = tr.find_element(By.TAG_NAME,"a")
                                        assigmnet_url = find_url.get_attribute('href')
                                        deadline = tr.find_element(By.CLASS_NAME, "cell.c2")
                                        submission_status = tr.find_element(By.CLASS_NAME, "cell.c3")

                                        assignments.append({
                                            'class_name': class_name,
                                            'assign_name': assignment.text,
                                            'deadline': deadline.text,
                                            'issubmit': 1 if "제출 완료" in submission_status.text else 0,
											'url' : assigment_url
											})
                                except Exception as e:
                                    print(f"과제 데이터 처리 중 오류: {e}")
                                    continue

                            # 창 닫고 다시 돌아가기 전에 확인
                            if len(self.driver.window_handles) > 1:
                                self.driver.close()
                                self.driver.switch_to.window(self.driver.window_handles[-1])

                        except Exception as e:
                            print(f"과제 페이지 처리 중 오류: {e}")

                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

                except Exception as e:
                    print(f"과목 처리 중 오류: {e}")
                    continue

        except Exception as e:
            print(f"전체 처리 중 오류 발생: {e}")
            # 모든 창을 안전하게 닫기
            while len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

        return assignments


    def close_connection(self):
        if self.driver:
            self.driver.quit()

