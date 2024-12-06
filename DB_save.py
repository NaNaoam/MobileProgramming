import mysql.connector

class AssignmentDatabase:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='220.68.54.167',
            user= 'yena',
            password='dlsvlslxm1994!',
            database='MP_team'
        )
        self.cursor = self.conn.cursor()

    def save_assignments(self, studno, assignments):
        for assignment in assignments:
            sql = '''
            INSERT INTO Assignment (studno, assignment_name, due_date, status)
            VALUES (%s, %s, %s, %s);
            '''
            status = 'Completed' if assignment['issubmit'] else 'Pending'
            values = (studno, assignment['assign_name'], assignment['deadline'], status )
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

