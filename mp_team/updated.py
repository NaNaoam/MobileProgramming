from flask import Flask, request, jsonify
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

class EclassCrawling:
    def __init__(self):
        self.driver = None

    def open_eclass(self):
        # Chrome 웹 드라이버 초기화
        self.driver = webdriver.Chrome()
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
        
        # 로그인 성공 여부 확인 (예: 페이지 URL이나 특정 요소 존재 여부 확인)
        if "login" not in self.driver.current_url:
            return True  # 로그인 성공
        else:
            return False  # 로그인 실패

    def open_calendar(self):
        # 캘린더 페이지 접근
        self.driver.get("https://ecampus.changwon.ac.kr/calendar/view.php?view=month&cal_m=11")
        time.sleep(2)
        
        # 예시로 일정 데이터를 가져와서 JSON 형태로 반환
        events = self.driver.find_elements(By.CLASS_NAME, "event")
        calendar_data = [event.text for event in events]
        return calendar_data

# 로그인 요청 처리 엔드포인트
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')

    eclass_service = EclassCrawling()
    eclass_service.open_eclass()

    if eclass_service.login(user_id, password):
        # 로그인 성공 시 캘린더 데이터 가져오기
        calendar_data = eclass_service.open_calendar()
        return jsonify({'status': 'success', 'message': 'Login successful!', 'calendar': calendar_data})
    else:
        # 로그인 실패 응답
        return jsonify({'status': 'failure', 'message': 'Invalid credentials'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)