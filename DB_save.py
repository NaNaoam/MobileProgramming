import mysql.connector
import json

class AssignmentDatabase:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='10.100.54.75',
            user='jinsoo',
            password='UXUZtd.HM77DE/h!',
            database='MP_team'
        )
        self.cursor = self.conn.cursor()

    def save_assignments(self, studno, assignments):
        for assignment in assignments:
            # 중복 체크
            check_sql = '''
            SELECT COUNT(*) FROM Assignment 
            WHERE studno = %s AND subjects = %s AND assign_name = %s
            '''
            check_values = (studno, assignment['class_name'], assignment['assign_name'])
            
            self.cursor.execute(check_sql, check_values)
            if self.cursor.fetchone()[0] > 0:
                continue  # 이미 존재하는 과제는 건너뛰기

            sql = '''
            INSERT INTO Assignment (studno, subjects, assign_name, deadline, issubmit, url)
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            values = (
                studno, 
                assignment['class_name'], 
                assignment['assign_name'], 
                assignment['deadline'], 
                '1' if assignment['issubmit'] == 1 else '0',
                assignment['url']
            )
            try:
                self.cursor.execute(sql, values)
                self.conn.commit()
            except mysql.connector.Error as err:
                print(f"DB 저장 실패: {err}")

    def fetch_assignments(self, studno=None):
        try:
            if studno:
                sql = """
                SELECT studno, subjects, assign_name, deadline, issubmit, url 
                FROM Assignment 
                WHERE studno = %s
                """
                self.cursor.execute(sql, (studno,))
            else:
                sql = """
                SELECT studno, subjects, assign_name, deadline, issubmit, url   
                FROM Assignment 
                """
                self.cursor.execute(sql)

            assignments = self.cursor.fetchall()
            
            assignment_list = []
            for assignment in assignments:
                assignment_list.append({
                    'studno': assignment[0],
                    'subjects': assignment[1],
                    'assign_name': assignment[2],
                    'deadline': assignment[3],
                    'issubmit': assignment[4],
                    'url': assignment[5]
                })
            return assignment_list
        except mysql.connector.Error as err:
            print(f"과제 조회 실패: {err}")
            return []

    def save_to_json(self, studno=None, filename='assignments.json'):
        try:
            assignments = self.fetch_assignments(studno)
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(assignments, json_file, ensure_ascii=False, indent=4)
            print(f"과제 정보를 {filename} 파일로 저장 완료!")
            return True
        except Exception as e:
            print(f"JSON 파일 저장 실패: {e}")
            return False

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()