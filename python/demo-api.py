##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2024/2025 ===============
## =============================================
## =================== Demo ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors:
##   João R. Campos <jrcampos@dei.uc.pt>
##   Nuno Antunes <nmsa@dei.uc.pt>
##   University of Coimbra


import flask
import logging
import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv
import datetime
import jwt
from functools import wraps
import hashlib
from flask import request

app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'some_jwt_secret_key'

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500,
    'unauthorized': 401
}


##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    
    try: 
        return psycopg2.connect(
            host = os.getenv("DB_HOST"),
            port= os.getenv("DB_PORT"),
            database= os.getenv("DB_NAME"),
            user= os.getenv("DB_USER"),
            password= os.getenv("DB_PASSWORD")
        )
    except:
        print("Couldn't connect to database!")
        

##########################################################
## AUTHENTICATION HELPERS
##########################################################

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = flask.request.headers.get('Authorization')
        
        if not token:
            return flask.jsonify({
                'status': StatusCodes['unauthorized'],
                'errors': 'Token is missing!',
                'results': None
            }),401

        try:
            # Remover 'Bearer ' do início se existir
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            data = jwt.decode(token,app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            flask.g.user = data  # opcional: guardar dados do utilizador
            
        except jwt.ExpiredSignatureError:
            return flask.jsonify({
                'status': StatusCodes['unauthorized'],
                'errors': 'Token expired!',
                'results': None
            }), 401
        except jwt.InvalidTokenError:
            return flask.jsonify({
                'status': StatusCodes['unauthorized'],
                'errors': 'Invalid token!',
                'results': None
            }), 401

        return f(*args, **kwargs)
    return decorated

def roles_required(*allowed_roles):
    
    def decorator(f):
        @wraps(f)
        
        def decorated(*args, **kwargs):
            user = flask.g.user      # user info got from decoding the jwt on the @token_required
            
            if user.get('role') not in allowed_roles:
                return flask.jsonify({
                    'status': StatusCodes['unauthorized'],
                    'errors': 'Access denied! You dont have credentials!',
                    'results': None
                }), 403
            return f(*args, **kwargs)
        
        return decorated
    return decorator


##########################################################
## ENDPOINTS
##########################################################

def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/dbproj/user', methods=['PUT'])
def login_user():
    data = request.get_json()

    if not data:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Missing JSON body',
            'results': None
        })

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Username and password are required',
            'results': None
        })

    conn = db_connection()
    if conn is None:
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': 'Database connection error',
            'results': None
        })

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                p.id,
                p.password,
                CASE
                    WHEN s.employee_person_id IS NOT NULL THEN 'staff'
                    WHEN i.employee_person_id IS NOT NULL THEN 'instructor'
                    WHEN st.person_id IS NOT NULL THEN 'student'
                    ELSE 'unknown'
                END AS role
            FROM person p
            LEFT JOIN staff s ON s.employee_person_id = p.id
            LEFT JOIN instructor i ON i.employee_person_id = p.id
            LEFT JOIN student st ON st.person_id = p.id
            WHERE p.name = %s
        """, (username,))

        result = cur.fetchone()
        
        if not result:
            return flask.jsonify({
                'status': StatusCodes['api_error'],
                'errors': 'Invalid credentials',
                'results': None
        })
    
        user_id, stored_password, role = result

        #ENCRYPT PASSWORDS ETC, SIMPLE FOR NOW
        
        if (password != stored_password):
            return flask.jsonify({
                'status': StatusCodes['api_error'],
                'errors': 'Invalid credentials',
                'results': None
            })

        token = jwt.encode({
            'user_id': user_id,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')

        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None,
            'results': token
        })

    except (Exception, psycopg2.DatabaseError) as e:
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(e),
            'results': None
        })

    finally:
        conn.close()

@app.route('/dbproj/register/student', methods=['POST'])
@token_required
@roles_required("staff")
def register_student():
    data = flask.request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get("password")
    date_of_birth_str = data.get('date_of_birth')
    district = data.get("district")
    
    if not username or not email or not password or not date_of_birth_str or not district:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Missing required fields!',
            'results': None
        })
    
    try:
        date_of_birth = datetime.datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
    except ValueError:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Invalid date format (YYYY-MM-DD)',
            'results': None
        })

    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None})

    try:
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO person (name, email, password,date_of_birth) 
                    VALUES (%s, %s, %s,%s) 
                    RETURNING id 
                    """, (username, email, password, date_of_birth))
        
        user_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO student (person_id, district)
            VALUES (%s, %s)
        """, (user_id, district))
        
        conn.commit()
        
        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None,
            'results': {'person_id': user_id, 'district': district}
        })
        
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/register/student - erro: {error}')
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': str(error), 'results': None})
    
    finally:
        if conn is not None:
            conn.close()


@app.route('/dbproj/register/staff', methods=['POST'])
@token_required
@roles_required("staff")
def register_staff():
    data = flask.request.get_json()


    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    date_of_birth_str = data.get('date_of_birth')
    hire_date_str = data.get('hire_date')
    salary = data.get('salary')
    status = data.get('status')
    roll = data.get('roll')

       
    if not username or not email or not password or not date_of_birth_str or not hire_date_str or not salary or not status or not roll:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Missing required fields!',
            'results': None
        })

    try:
        date_of_birth = datetime.datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        hire_date = datetime.datetime.strptime(hire_date_str, '%Y-%m-%d').date()
    except ValueError:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Invalid date format (YYYY-MM-DD)',
            'results': None
        })
        
    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None})

    try: 
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO person (name, email, password,date_of_birth) 
                    VALUES (%s, %s, %s,%s) 
                    RETURNING id 
                    """, (username, email, password, date_of_birth))
        
        user_id = cur.fetchone()[0]
        
        cur.execute("""INSERT INTO employee (person_id,hire_date,salary,status)
                    VALUES (%s, %s, %s, %s) 
                    """,(user_id, hire_date, salary, status))

        cur.execute("""
                    INSERT INTO staff (roll,employee_person_id)
                    VALUES (%s,%s)""",(roll,user_id))

        conn.commit()
        
        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None,
            'results': user_id
        })

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/register/staff - erro: {error}')
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        })

    finally:
        conn.close()

@app.route('/dbproj/register/instructor', methods=['POST'])
@token_required
@roles_required("staff")
def register_instructor():
    data = flask.request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    date_of_birth_str = data.get('date_of_birth')
    hire_date_str = data.get('hire_date')
    salary = data.get('salary')
    status = data.get('status')
       
    if not username or not email or not password or not date_of_birth_str or not hire_date_str or not salary or not status:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Missing required fields!',
            'results': None
        })

    try:
        date_of_birth = datetime.datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        hire_date = datetime.datetime.strptime(hire_date_str, '%Y-%m-%d').date()
    except ValueError:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Invalid date format (YYYY-MM-DD)',
            'results': None
        })
        
    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None})

    try: 
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO person (name, email, password,date_of_birth) 
                    VALUES (%s, %s, %s,%s) 
                    RETURNING id 
                    """, (username, email, password, date_of_birth))
        
        user_id = cur.fetchone()[0]
        
        cur.execute("""INSERT INTO employee (person_id,hire_date,salary,status)
                    VALUES (%s, %s, %s, %s) 
                    """,(user_id, hire_date, salary, status))

        cur.execute("""
                    INSERT INTO instructor (employee_person_id)
                    VALUES (%s)
                    """,(user_id,))

        conn.commit()
        
        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None,
            'results': user_id
        })

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/register/staff - erro: {error}')
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        })

    finally:
        conn.close()

@app.route('/dbproj/enroll_degree/<degree_id>', methods=['POST'])
@token_required
@roles_required("staff")
def enroll_degree(degree_id):

    data = flask.request.get_json()
    
    person_id = data.get('student_id')
    date_str = data.get('date')
    
    if not person_id or not date_str:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Student ID and date are required',
            'results': None
        }), 400
        
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Invalid date format (YYYY-MM-DD)',
            'results': None
        })
        

    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None})

    try:
        cur = conn.cursor()
        
        cur.execute("""INSERT INTO enrollment (enrollment_date_,status,student_person_id)
                    VALUES (%s, %s, %s) 
                    RETURNING enrollment_id""",(date,"ON", person_id))
        
        enrollment_id = cur.fetchone()
        
        cur.execute("""INSERT INTO degree_enrollment (average_grade,approved_courses_count, degree_degree_id , enrollment_enrollment_id)
                    VALUES (%s, %s, %s,%s)""",(0.0, 0, degree_id,enrollment_id))
        
        conn.commit()
        
        response = {'status': StatusCodes['success'], 'errors': None, 'results': "Student enrolled in degree!"}
        return flask.jsonify(response), 201
    
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/enroll_degree/{degree_id} - erro: {error}')
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        })
        
    finally:
        if conn is not None:
            conn.close()

@app.route('/dbproj/enroll_activity/<activity_id>', methods=['POST'])
@token_required
@roles_required("student")
def enroll_activity(activity_id):

    data = flask.request.get_json()
    
    person_id = data.get('student_id')
    date_str = data.get('date')

    if not person_id or not date_str:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Student ID and date are required',
            'results': None
    }), 400
        
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Invalid date format (YYYY-MM-DD)',
            'results': None
        })
        
        
    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None})

    try:
        cur = conn.cursor()
        
        cur.execute("""INSERT INTO enrollment (enrollment_date_,status,student_person_id)
                    VALUES (%s, %s, %s) 
                    RETURNING enrollment_id""",(date,"ON", person_id))
        
        enrollment_id = cur.fetchone()
        
        cur.execute(
            'INSERT INTO extraactivity_enrollment (extraactivity_activity_id, enrollment_enrollment_id) VALUES (%s, %s)',
            (activity_id, enrollment_id)
        )
        
        conn.commit()
        
        response = {'status': StatusCodes['success'], 'errors': None, 'results': "Student enrolled in extra_activity"}
        return flask.jsonify(response)
    
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/enroll_activity/{activity_id} - erro: {error}')
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        })
        
    finally:
        if conn is not None:
            conn.close()

@app.route('/dbproj/enroll_course_edition/<course_edition_id>', methods=['POST'])
@token_required
@roles_required("student")
def enroll_course_edition(course_edition_id):
    user = flask.g.user  # token decodificado no @token_required

    # Apenas estudantes podem se inscrever em edições de curso
    if user.get('user_type') != 'student':
        return flask.jsonify({
            'status': StatusCodes['unauthorized'],
            'errors': 'Only students can enroll in course editions',
            'results': None
        }), 401

    data = flask.request.get_json()
    classes = data.get('classes', [])
    date_str= data.get('date')
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


    if not classes:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'At least one class ID is required',
            'results': None
        })

    student_id = user.get('user_id')
    if not student_id:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Student ID not found in token',
            'results': None
        })

    conn = db_connection()
    if conn is None:
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': 'Erro de conexão com o banco',
            'results': None
        })

    try:
        cur = conn.cursor()
    
        cur.execute(
            'INSERT INTO enrollment (enrollment_date_,status,student_financialaccount_person_id) VALUES (%s, %s, %s) RETURNING enrollment_id',(date,"ON", student_id))
        enrollment_id = cur.fetchone()
        
        cur.execute(
            'INSERT INTO course_enrollment (grade,approved,courseedition_edition_id,enrollment_enrollment_id) VALUES (%s, %s, %s,%s)',(0,False,course_edition_id, enrollment_id))
                
        for class_id in classes:
            cur.execute(
                'INSERT INTO class_enrollment (class_id) VALUES (%s)',
                (class_id)
            )
        conn.commit()
        response = {'status': StatusCodes['success'], 'errors': None, 'results': None}
        return flask.jsonify(response)
    
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/enroll_course_edition/{course_edition_id} - erro: {error}')
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        })
    finally:
        if conn is not None:
            conn.close()


@app.route('/dbproj/delete_details/<person_id>', methods=['DELETE'])
@token_required
@roles_required("staff")
def delete_student(person_id):

    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None})
    
    try:
        cur = conn.cursor()
        

        cur.execute("""
            DELETE FROM degree_enrollment de
            USING enrollment e
            WHERE de.enrollment_enrollment_id = e.enrollment_id
              AND e.student_person_id = %s
        """, (person_id,))
        
        cur.execute("""
            DELETE FROM extraactivity_enrollment ee
            USING enrollment e
            WHERE ee.enrollment_enrollment_id = e.enrollment_id
              AND e.student_person_id = %s
        """, (person_id,))
        
        cur.execute("""
            DELETE FROM enrollment
            WHERE student_person_id = %s
        """, (person_id,))

        cur.execute("""
            DELETE FROM student
            WHERE person_id = %s
        """, (person_id,))
        
        cur.execute("""
            DELETE FROM person
            WHERE id = %s
        """, (person_id,))
        
        conn.commit()
        
        response = {'status': StatusCodes['success'], 'errors': None, 'results': "Student eliminated!"}
        return flask.jsonify(response), 200
        
    except Exception as error:
        conn.rollback()
        logger.error(f'DELETE /dbproj/delete_details/{person_id} - erro: {error}')
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': str(error), 'results': None}), 500
        
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    
    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API stubs online: http://{host}:{port}')
