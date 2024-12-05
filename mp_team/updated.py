# from flask import Flask, request, jsonify
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import time

# app = Flask(__name__)

# class EclassCrawling:
#     def __init__(self):
#         self.driver = None

#     def open_eclass(self):
#         # Chrome 웹 드라이버 초기화
#         self.driver = webdriver.Chrome()
#         self.driver.set_page_load_timeout(10)
    
#     def login(self, user_id, password):
#         # E-campus 로그인 페이지 접근
#         self.driver.get("https://ecampus.changwon.ac.kr/login.php")
#         time.sleep(2)  # 페이지 로딩 대기
        
#         # 아이디와 비밀번호 입력 및 로그인 시도
#         self.driver.find_element(By.ID, "input-username").send_keys(user_id)
#         self.driver.find_element(By.ID, "input-password").send_keys(password)
#         self.driver.find_element(By.NAME, "loginbutton").click()
#         time.sleep(2)
        
#         # 로그인 성공 여부 확인 (예: 페이지 URL이나 특정 요소 존재 여부 확인)
#         if "login" not in self.driver.current_url:
#             return True  # 로그인 성공
#         else:
#             return False  # 로그인 실패

#     def open_calendar(self):
#         # 캘린더 페이지 접근
#         self.driver.get("https://ecampus.changwon.ac.kr/calendar/view.php?view=month&cal_m=11")
#         time.sleep(2)
        
#         # 예시로 일정 데이터를 가져와서 JSON 형태로 반환
#         events = self.driver.find_elements(By.CLASS_NAME, "event")
#         calendar_data = [event.text for event in events]
#         return calendar_data

# # 로그인 요청 처리 엔드포인트
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user_id = data.get('id')
#     password = data.get('password')

#     eclass_service = EclassCrawling()
#     eclass_service.open_eclass()

#     if eclass_service.login(user_id, password):
#         # 로그인 성공 시 캘린더 데이터 가져오기
#         calendar_data = eclass_service.open_calendar()
#         return jsonify({'status': 'success', 'message': 'Login successful!', 'calendar': calendar_data})
#     else:
#         # 로그인 실패 응답
#         return jsonify({'status': 'failure', 'message': 'Invalid credentials'})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException

app = Flask(__name__)

class EclassCrawling:
    def __init__(self):
        self.driver = None
        self.class_list = {}

    def open_eclass(self):
        # Chrome 웹 드라이버 초기화
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.set_page_load_timeout(10)

    def login(self, user_id, password):
        # E-campus 로그인 페이지 접근
        self.driver.get("https://ecampus.changwon.ac.kr/login.php")
        time.sleep(2)  # 페이지 로딩 대기

        # 아이디와 비밀번호 입력 및 로그인 시도
        self.driver.find_element(By.ID, "input-username").send_keys(user_id)
        self.driver.find_element(By.ID, "input-password").send_keys(password)
        self.driver.find_element(By.NAME, "loginbutton").click()
        time.sleep(2)

        # 로그인 성공 여부 확인
        if "login" not in self.driver.current_url:
            return True  # 로그인 성공
        else:
            return False  # 로그인 실패

    def open_class(self):
        try:
            ul_element = self.driver.find_element(By.CLASS_NAME, "my-course-lists.coursemos-layout-0")
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")

            for i in li_elements:
                class_name = i.find_element(By.CLASS_NAME, "course-title").text
                self.class_list[class_name] = None

                a_element = i.find_element(By.TAG_NAME, "a")
                href = a_element.get_attribute('href')
                self.driver.execute_script("window.open(arguments[0]);", href)
                new_window = self.driver.window_handles[-1]
                self.driver.switch_to.window(new_window)

                time.sleep(1)
                xpath = "//li/a[contains(text(),'과제')]"
                assignment_elements = self.driver.find_elements(By.XPATH, xpath)

                if assignment_elements:
                    div_element = self.driver.find_element(By.CLASS_NAME, "block.block-coursemos.block-quick-mod")
                    li_element_2 = div_element.find_element(By.TAG_NAME, "li")
                    href_ar = li_element_2.find_element(By.TAG_NAME, "a").get_attribute('href')
                    print(f"과제 링크: {href_ar}")
                else:
                    print("과제를 찾을 수 없습니다.")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            print(f"오류 발생: {e}")
        return self.class_list

# Flask 라우트 설정
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')

    # E-class 크롤링 실행
    eclass_service = EclassCrawling()
    eclass_service.open_eclass()

    if eclass_service.login(user_id, password):
        class_data = eclass_service.open_class()
        return jsonify({'status': 'success', 'message': 'Login successful!', 'classes': class_data})
    else:
        return jsonify({'status': 'failure', 'message': 'Invalid credentials'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)