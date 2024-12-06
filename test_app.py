from flask import Flask, request, jsonify
from crawler import EclassCrawler 
from DB_save import AssignmentDatabase
app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')

    eclass_service = EclassCrawler(studno=user_id)
    assignment_db = AssignmentDatabase()
    
    
    
    try:
        eclass_service.open_eclass()
        if eclass_service.login(user_id, password):
            assignments = eclass_service.open_class()
            assignment_db.save_assignments(user_id, assignments)
            assignment_db.save_to_json()
            return jsonify({'status': 'success', 'message': 'Assignment data successfully saved!'})
        else:
            return jsonify({'status': 'failure', 'message': 'Invalid credentials'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        eclass_service.close_connection()
        assignment_db.close_connection()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

