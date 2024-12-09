
from flask import Flask, request, jsonify, Response
from crawler import EclassCrawler 
from DB_save import AssignmentDatabase
from flask_cors import CORS
import json
#import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
#logging.basicConfig(level=logging.DEBUG)
#app.logger.setLevel(logging.DEBUG)

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
        if not data:
            app.logger.error("데이터가 없음")
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        #app.logger.debug(f"Received login request with data: {data}")

        user_id = data.get('id')
        password = data.get('password')
        
        app.logger.info(f"ID: {user_id}, Password: {'*' * len(password)}")

        if not user_id or not password:
            app.logger.error("ID 또는 비밀번호 누락")
            return jsonify({
                'status': 'error',
                'message': 'Missing id or password'
            }), 400

        eclass_service = EclassCrawler(studno=user_id)
        assignment_db = AssignmentDatabase()
        
        try:
            eclass_service.open_eclass()
        #     if eclass_service.login(user_id, password):
        #         assignments = eclass_service.open_class()
        #         if assignments and isinstance(assignments, list):
        #             assignment_db.save_assignments(user_id, assignments)
        #             assignment_db.save_to_json()
        #             response_data = {
        #                 'status': 'success',
        #                 'message': 'Assignment data successfully saved!'
        #             }
        #             return Response(
        #                 json.dumps(response_data),
        #                 status=200,
        #                 mimetype='application/json'
        #             )
        #         else:
        #             response_data = {
        #                 'status': 'error',
        #                 'message': 'No assignments found or invalid data format'
        #             }
        #     else:
        #         response_data = {
        #             'status': 'failure',
        #             'message': 'Invalid credentials'
        #         }
        # except Exception as e:
        #     response_data = {
        #         'status': 'error',
        #         'message': str(e)
        #     }
        # finally:
        #     try:
        #         eclass_service.close_connection()
        #         assignment_db.close_connection()
        #     except:
        #         pass
            if eclass_service.login(user_id, password):
                assignments = eclass_service.open_class()
                if assignments and isinstance(assignments, list):
                    assignment_db.save_assignments(user_id, assignments)
                    assignment_db.save_to_json()
                    return jsonify({
                        'status': 'success',
                        'message': 'Assignment data successfully saved!'
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'No assignments found or invalid data format'
                    })
            else:
                return jsonify({
                    'status': 'failure',
                    'message': 'Invalid credentials'
                })
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
        finally:
            try:
                eclass_service.close_connection()
                assignment_db.close_connection()
            except:
                pass

    except Exception as e:
        app.logger.error(f"에러 발생: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

    return Response(
        json.dumps(response_data),
        status=400 if response_data['status'] == 'error' else 200,
        mimetype='application/json'
    )

@app.route('/fetch-assignments/<studno>', methods=['POST'])
def fetch_assignments(studno):
    try:
        # GET 요청의 경우
        if request.method == 'GET':
            assignment_db = AssignmentDatabase()
            assignments = assignment_db.fetch_assignments(studno)
            return jsonify({
                'status': 'success',
                'assignments': assignments
            })
        
        # POST 요청의 경우 (기존 코드)
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'status': 'error',
                'message': 'Password is required'
            })

        eclass_service = EclassCrawler(studno=studno)
        assignment_db = AssignmentDatabase()
        
        try:
            eclass_service.open_eclass()
            if eclass_service.login(studno, password):
                assignments = eclass_service.open_class()
                if assignments and isinstance(assignments, list):
                    assignment_db.save_assignments(studno, assignments)
                    return jsonify({
                        'status': 'success',
                        'message': 'Assignments fetched successfully'
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'No assignments found or invalid data format'
                    })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Login failed'
                })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            })
        finally:
            eclass_service.close_connection()
            assignment_db.close_connection()
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
        # 여기서 크롤링 상태를 확인하는 로직 구현
        # 예시로 항상 성공으로 반환
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