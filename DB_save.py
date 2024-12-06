import mysql.connector
import json

class AssignmentDatabase:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='10.100.54.167',
            user= 'yena',
            password='dlsvlslxm1994!',
            database='MP_team'
        )
        self.cursor = self.conn.cursor()

    def save_assignments(self, studno, assignments):
        for assignment in assignments:
            sql = '''
            INSERT INTO Assignment (studno, class_name,assignment_name, deadline, status)
            VALUES (%s,  %s,%s, %s, %s);
            '''
            status = 'Completed' if assignment['issubmit'] else 'Pending'
            values = (studno, assignment['class_name'],assignment['assign_name'], assignment['deadline'], status )
            try:
                self.cursor.execute(sql, values)
                self.conn.commit()
                print(f"과제 '{assignment['assign_name']}' 저장 성공!")
            except mysql.connector.Error as err:
                print(f"DB 저장 실패: {err}")

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


    def fetch_assignments(self):
        # 데이터베이스에서 과제 정보 가져오기
        sql = "SELECT studno, class_name,assignment_name, deadline, status FROM Assignment"
        self.cursor.execute(sql)
        assignments = self.cursor.fetchall()
        
        # 데이터를 딕셔너리로 변환
        assignment_list = []
        for assignment in assignments:
            assignment_list.append({
                'studno': assignment[0],
                'class_name' : assignment[1],
                'assignment_name': assignment[2],
                'deadline': assignment[3],
                'status': assignment[4]
            })
        return assignment_list

    def save_to_json(self, filename='assignments.json'):
        # JSON 파일로 저장
        assignments = self.fetch_assignments()
        with open(filename, 'w') as json_file:
            json.dump(assignments, json_file, indent=4, ensure_ascii=False)
        print(f"과제 정보를 {filename} 파일로 저장 완료!")



