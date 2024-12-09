
from flask import Flask, request, jsonify, Response
from crawler import EclassCrawler 
from DB_save import AssignmentDatabase
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({
        'status': 'success',
        'message': 'Server is running',
        'available_endpoints': [
            '/login [POST]',
            '/fetch-assignments/<studno> [POST]',
            '/check-crawling-status/<studno> [GET]'
        ]
    })

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_id = data.get('id')
        password = data.get('password')

        if not user_id or not password:
            return jsonify({
                'status': 'error',
                'message': 'Missing id or password'
            }), 400

        eclass_service = EclassCrawler(studno=user_id)
        try:
            eclass_service.open_eclass()
            if eclass_service.login(user_id, password):
                assignments = eclass_service.open_class()
                if assignments and isinstance(assignments, list):
                    return jsonify({
                        'status': 'success',
                        'assignments': assignments
                    })
            return jsonify({
                'status': 'error',
                'message': 'Login failed or no assignments found'
            })
        finally:
            eclass_service.close_connection()
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/fetch-assignments/<studno>', methods=['POST'])
def fetch_assignments(studno):
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'status': 'error',
                'message': 'Password is required'
            })

        eclass_service = EclassCrawler(studno=studno)
        
        try:
            eclass_service.open_eclass()
            if eclass_service.login(studno, password):
                assignments = eclass_service.open_class()
                if assignments and isinstance(assignments, list):
                    # 바로 assignments 반환
                    return jsonify({
                        'status': 'success',
                        'assignments': assignments
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'No assignments found'
                    })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Login failed'
                })
        finally:
            eclass_service.close_connection()
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@app.route('/assignments/<studno>', methods=['GET'])
def get_assignments(studno):
    try:
        assignment_db = AssignmentDatabase()
        assignments = assignment_db.fetch_assignments(studno)
        return jsonify({
            'status': 'success',
            'assignments': assignments
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/check-crawling-status/<studno>', methods=['GET'])
def check_crawling_status(studno):
    try:
        # 크롤링 상태를 확인
        return jsonify({
            'status': 'success',
            'message': 'Crawling completed'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5004,
        debug=True,
        threaded=True
    )