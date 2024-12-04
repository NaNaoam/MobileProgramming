import mysql.connector
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

app = Flask(__name__)

class EclassCrawling:
    def __init__(self, studno):
        self.driver = None
        self.class_list = {}
        self.studno = studno

        # MariaDB 연결
        self.conn = mysql.connector.connect(
            host='10.100.54.75',
            user='jinsoo',
            password='UXUZtd.HM77DE/h!',
            database='MP_team'
        )

        self.cursor = self.conn.cursor()

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
        try:
            ul_element = self.driver.find_element(By.CLASS_NAME, "my-course-lists.coursemos-layout-0")
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")

            for i in li_elements:
                try:
                    class_findname = i.find_element(By.CLASS_NAME, "course-title")
                    class_name = class_findname.find_element(By.TAG_NAME, "h3").text
                    print(f"과목명: {class_name} 처리 시작")  # 디버깅용 로그
                    
                    a_element = i.find_element(By.TAG_NAME, "a")
                    href = a_element.get_attribute('href')
                    self.driver.execute_script("window.open(arguments[0]);", href)
                    new_window = self.driver.window_handles[-1]
                    self.driver.switch_to.window(new_window)
                    
                    # 페이지 로딩 대기 시간 증가
                    WebDriverWait(self.driver, 20).until(
                        lambda driver: driver.execute_script('return document.readyState') == 'complete'
                    )

                    xpath = "//li/a[contains(text(),'과제')]"
                    assignment_elements = self.driver.find_elements(By.XPATH, xpath)

                    if assignment_elements:
                        print("과제 페이지 발견")  # 디버깅용 로그
                        
                        # 과제 페이지 로딩 대기
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
                            
                            # 과제 목록 페이지 로딩 대기
                            WebDriverWait(self.driver, 20).until(
                                lambda driver: driver.execute_script('return document.readyState') == 'complete'
                            )

                            # tbody 요소를 찾기 전에 명시적 대기 추가
                            try:
                                tbody_elements = WebDriverWait(self.driver, 10).until(
                                    lambda x: x.find_element(By.TAG_NAME, "tbody")
                                )
                                tr_elements = tbody_elements.find_elements(By.TAG_NAME, "tr")
                                print(f"발견된 과제 행 수: {len(tr_elements)}")  # 디버깅용 로그

                                for tr in tr_elements:
                                    try:
                                        td_elements = tr.find_elements(By.TAG_NAME, "td")
                                        if len(td_elements) > 3:
                                            assignment = tr.find_element(By.CLASS_NAME, "cell.c1")
                                            deadline = tr.find_element(By.CLASS_NAME, "cell.c2")
                                            submission_status = tr.find_element(By.CLASS_NAME, "cell.c3")
                                            
                                            print(f"과제명: {assignment.text}")  # 디버깅용 로그
                                            
                                            # DB에 데이터 삽입
                                            sql = '''
                                            INSERT INTO Assignment (studno, assign_name, subjects, deadline, isdeleted, issubmit)
                                            VALUES (%s, %s, %s, %s, %s, %s);
                                            '''
                                            issubmit = 1 if "제출 완료" in submission_status.text else 0
                                            values = (self.studno, assignment.text, class_name, deadline.text, 0, issubmit)
                                            
                                            try:
                                                self.cursor.execute(sql, values)
                                                self.conn.commit()
                                                print(f"과제 '{assignment.text}' 저장 성공!")
                                            except mysql.connector.Error as err:
                                                print(f"DB 저장 실패: {err}")
                                    except Exception as e:
                                        print(f"과제 데이터 처리 중 오류: {e}")
                                        continue
                            except Exception as e:
                                print(f"tbody 요소를 찾을 수 없음: {e}")
                        
                            self.driver.close()
                            self.driver.switch_to.window(new_window)
                        except Exception as e:
                            print(f"과제 페이지 처리 중 오류: {e}")
                    
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                except Exception as e:
                    print(f"과목 처리 중 오류: {e}")
                    continue

        except Exception as e:
            print(f"전체 처리 중 오류 발생: {e}")
            # 에러 발생 시 열린 창들 정리
            while len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        if self.driver:
            self.driver.quit()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')

    eclass_service = EclassCrawling(studno=user_id)
    try:
        eclass_service.open_eclass()
        if eclass_service.login(user_id, password):
            eclass_service.open_class()
            return jsonify({'status': 'success', 'message': 'Assignment data successfully saved!'})
        else:
            return jsonify({'status': 'failure', 'message': 'Invalid credentials'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        eclass_service.close_connection()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)