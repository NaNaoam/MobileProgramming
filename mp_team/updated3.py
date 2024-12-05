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
import os
os.environ['WDM_LOG_LEVEL'] = '0'  # WebDriver Manager 로그 레벨 설정
from flask_cors import CORS
from werkzeug.serving import WSGIRequestHandler


app = Flask(__name__)

# 서버 타임아웃 설정 증가
WSGIRequestHandler.protocol_version = "HTTP/1.1"
app.config['TIMEOUT'] = 600  # 10분

# CORS 설정 추가

CORS(app)


from threading import Thread
from queue import Queue

# 결과를 저장할 전역 딕셔너리
crawling_results = {}

# def background_crawling(user_id):
#     eclass_service = EclassCrawling(studno=user_id)
#     try:
#         eclass_service.open_eclass()
#         eclass_service.open_class()
#         crawling_results[user_id] = "success"
#     except Exception as e:
#         crawling_results[user_id] = str(e)
#     finally:
#         if hasattr(eclass_service, 'driver'):
#             eclass_service.driver.quit()

# @app.route('/fetch-assignments/<studno>', methods=['POST'])
# def fetch_assignments(studno):
#     # 백그라운드에서 크롤링 시작
#     thread = Thread(target=background_crawling, args=(studno,))
#     thread.daemon = True
#     thread.start()
    
#     return jsonify({
#         'status': 'processing',
#         'message': 'Crawling started'
#     })

def background_crawling(user_id, password):  # password 파라미터 추가
    eclass_service = EclassCrawling(studno=user_id)
    try:
        eclass_service.open_eclass()
        # 로그인 추가
        if eclass_service.login(user_id, password):
            eclass_service.open_class()
            crawling_results[user_id] = "success"
        else:
            crawling_results[user_id] = "Login failed"
    except Exception as e:
        crawling_results[user_id] = str(e)
    finally:
        if hasattr(eclass_service, 'driver'):
            eclass_service.driver.quit()

@app.route('/fetch-assignments/<studno>', methods=['POST'])
def fetch_assignments(studno):
    # 요청에서 비밀번호를 받아옴
    data = request.get_json()
    password = data.get('password')
    
    if not password:
        return jsonify({
            'status': 'error',
            'message': 'Password is required'
        })
    
    # 백그라운드에서 크롤링 시작 (비밀번호 전달)
    thread = Thread(target=background_crawling, args=(studno, password))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'processing',
        'message': 'Crawling started'
    })

@app.route('/check-crawling-status/<studno>', methods=['GET'])
def check_crawling_status(studno):
    result = crawling_results.get(studno)
    if result is None:
        return jsonify({
            'status': 'processing',
            'message': 'Still processing'
        })
    elif result == "success":
        # 크롤링 완료 후 결과 삭제
        del crawling_results[studno]
        return jsonify({
            'status': 'success',
            'message': 'Crawling completed'
        })
    else:
        # 에러 발생 시
        del crawling_results[studno]
        return jsonify({
            'status': 'error',
            'message': result
        })

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

        self.cursor = self.conn.cursor(buffered=True)

    def open_eclass(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--log-level=3')  # 심각한 에러만 표시
        chrome_options.add_argument('--silent')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()
                            , log_output=os.devnull),
            options=chrome_options
        )
        #self.driver.set_page_load_timeout(20)  # 타임아웃도 20초로 증가
        #driver = webdriver.Chrome(service=service, options=chrome_options)

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
            # 메인 페이지 로딩 대기
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
                    # 명시적 대기 조건 추가
            wait = WebDriverWait(self.driver, 30)
            wait.until(lambda x: x.find_element(By.CLASS_NAME, "my-course-lists.coursemos-layout-0"))

            # 과목 목록 찾기
            try:
                ul_element = WebDriverWait(self.driver, 10).until(
                    lambda x: x.find_element(By.CLASS_NAME, "my-course-lists.coursemos-layout-0")
                )
                li_elements = ul_element.find_elements(By.TAG_NAME, "li")
                print(f"발견된 과목 수: {len(li_elements)}")

                for i in li_elements:
                    try:
                        # 과목명 찾기
                        class_findname = WebDriverWait(i, 10).until(
                            lambda x: x.find_element(By.CLASS_NAME, "course-title")
                        )
                        class_name = WebDriverWait(class_findname, 10).until(
                            lambda x: x.find_element(By.TAG_NAME, "h3")
                        ).text
                        print(f"과목명: {class_name} 처리 시작")

                        # 과목 링크 클릭
                        a_element = WebDriverWait(i, 10).until(
                            lambda x: x.find_element(By.TAG_NAME, "a")
                        )
                        href = a_element.get_attribute('href')
                        print(f"과목 URL: {href}")

                        # 새 창에서 과목 페이지 열기
                        self.driver.execute_script("window.open(arguments[0]);", href)
                        #time.sleep(2)  # 창이 열릴 때까지 대기
                        WebDriverWait(self.driver, 10).until(
        lambda driver: driver.execute_script('return document.readyState') == 'complete'
    )
                        new_window = self.driver.window_handles[-1]
                        self.driver.switch_to.window(new_window)

                        # 과목 페이지 로딩 대기
                        WebDriverWait(self.driver, 20).until(
                            lambda driver: driver.execute_script('return document.readyState') == 'complete'
                        )
                        #time.sleep(2)  # 추가 대기 시간
                        WebDriverWait(self.driver, 10).until(
    lambda driver: driver.execute_script('return document.readyState') == 'complete'
)

                        # 과제 메뉴 찾기 및 클릭
                        try:
                            assignment_elements = WebDriverWait(self.driver, 10).until(
                                lambda x: x.find_elements(By.XPATH, "//li/a[contains(text(),'과제')]")
                            )
                            if assignment_elements:
                                print("과제 메뉴 발견")
                                assignment_elements[0].click()
                                #time.sleep(2)  # 클릭 후 대기
                                WebDriverWait(self.driver, 10).until(
                                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                                )

                                # 과제 테이블 찾기
                                try:        #정상적으로 실행X
                                    table = WebDriverWait(self.driver, 10).until(
                                        lambda x: x.find_element(By.CSS_SELECTOR, ".generaltable")
                                    )
                                    # tr_elements = table.find_elements(By.TAG_NAME, "tr")
                                    # print(f"발견된 과제 행 수: {len(tr_elements)}")
                                    if not table:
                                        print("과제 테이블이 없습니다.")
                                        return
                                        
                                    print("과제 테이블 찾음")  # 디버깅용
                                    
                                    # # 페이지 소스 출력하여 실제 테이블 존재 확인
                                    # print(self.driver.page_source)
                                    
                                    tr_elements = table.find_elements(By.TAG_NAME, "tr")
                                    print(f"발견된 과제 행 수: {len(tr_elements)}")

                                    for tr in tr_elements[1:]:  # 헤더 제외
                                        try:
                                            td_elements = tr.find_elements(By.TAG_NAME, "td")
                                            if len(td_elements) > 3:
                                                assignment_text = td_elements[1].text.strip()
                                                deadline_text = td_elements[2].text.strip()
                                                submission_status = td_elements[3].text.strip()
                                                
                                                print(f"과제명: {assignment_text}")
                                                print(f"마감일: {deadline_text}")
                                                print(f"제출상태: {submission_status}")

                                                check_sql = '''
                                                SELECT assignment_id 
                                                FROM Assignment 
                                                WHERE studno = %s 
                                                AND assign_name = %s 
                                                AND subjects = %s 
                                                AND deadline = %s
                                                '''
                                                try:
                                                    self.cursor.execute(check_sql, (self.studno, assignment_text, class_name, deadline_text))
                                                    existing_record = self.cursor.fetchone()

                                                    if not existing_record:
                                                        insert_sql = '''
                                                        INSERT INTO Assignment 
                                                        (studno, assign_name, subjects, deadline, isdeleted, issubmit)
                                                        VALUES (%s, %s, %s, %s, %s, %s)
                                                        '''
                                                        issubmit_value = "1" if "제출 완료" in submission_status else "0"
                                                        values = (
                                                            self.studno, 
                                                            assignment_text, 
                                                            class_name, 
                                                            deadline_text, 
                                                            "0",  # isdeleted를 VARCHAR로 변경했으므로 문자열로 전달
                                                            issubmit_value  # issubmit도 VARCHAR로 변경했으므로 문자열로 전달
                                                        )
                                                        self.cursor.execute(insert_sql, values)
                                                        self.conn.commit()
                                                        print(f"과제 '{assignment_text}' 저장 성공!")
                                                    else:
                                                        print(f"과제 '{assignment_text}' 이미 존재함")
                                                except mysql.connector.Error as err:
                                                    print(f"DB 작업 중 오류 발생: {err}")

                                        except Exception as e:
                                            print(f"과제 데이터 처리 중 오류: {e}")
                                            continue

                                except Exception as e:          
                                    print(f"과제 테이블을 찾을 수 없음: {e}")

                        except Exception as e:
                            print(f"과제 메뉴를 찾을 수 없음: {e}")

                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])

                    except Exception as e:
                        print(f"과목 처리 중 오류: {e}")
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        continue

            except Exception as e:
                print(f"과목 목록을 찾을 수 없음: {e}")

        except Exception as e:
            print(f"전체 처리 중 오류 발생: {e}")
            # 열린 창 모두 닫기
            while len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def close_connection(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"리소스 해제 중 오류 발생: {e}")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')
    
    eclass_service = EclassCrawling(studno=user_id)
    try:
        eclass_service.open_eclass()
        if eclass_service.login(user_id, password):
            # 로그인 성공시 바로 응답 반환
            return jsonify({
                'status': 'success', 
                'message': 'Login successful',
                'studno': user_id
            })
        else:
            return jsonify({'status': 'failure', 'message': 'Invalid credentials'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        if hasattr(eclass_service, 'driver') and eclass_service.driver:
            eclass_service.driver.quit()

@app.route('/assignments/<studno>', methods=['GET'])
def get_assignments(studno):
    try:
        conn = mysql.connector.connect(
            host='10.100.54.75',
            user='jinsoo',
            password='UXUZtd.HM77DE/h!',
            database='MP_team'
        )
        cursor = conn.cursor(dictionary=True)
        
        sql = '''
        SELECT assign_name, subjects, deadline, issubmit 
        FROM Assignment 
        WHERE studno = %s AND isdeleted = 0 
        ORDER BY deadline ASC
        '''
        cursor.execute(sql, (studno,))
        assignments = cursor.fetchall()
        
        return jsonify({
            'status': 'success',
            'assignments': assignments
        })
        
    except Exception as e:
        print(f"과제 조회 중 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)