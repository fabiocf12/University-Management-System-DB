##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2024/2025 ===============
## =============================================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors:
##   Fábio Fernandess - nº 2023230805 <fcfernandes2005@gmail.com>


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

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')


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

            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            data = jwt.decode(token,app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            flask.g.user = data  
            
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

#Helper function
def insert_person(cursor, data):
    cursor.execute("""
                INSERT INTO person (name, email, password,date_of_birth) 
                VALUES (%s, %s, %s,%s) 
                RETURNING id 
                """, (data.get('username'), data.get('email'), data.get("password"), data.get('date_of_birth')))
    
    user_id = cursor.fetchone()[0]
    return user_id


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

    hashed_attempt = encrypt_password(password)

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
                    WHEN s.person_id IS NOT NULL THEN 'staff'
                    WHEN i.person_id IS NOT NULL THEN 'instructor'
                    WHEN st.person_id IS NOT NULL THEN 'student'
                    ELSE 'unknown' 
                END AS role
            FROM person p
            LEFT JOIN staff s ON s.person_id = p.id
            LEFT JOIN instructor i ON i.person_id = p.id
            LEFT JOIN student st ON st.person_id = p.id
            WHERE p.email = %s
        """, (username,))

        result = cur.fetchone()
        
        if not result:
            return flask.jsonify({
                'status': StatusCodes['api_error'],
                'errors': 'Invalid credentials',
                'results': None
        })
    
        user_id, stored_password, role = result
        
        if (hashed_attempt != stored_password):
            return flask.jsonify({
                'status': StatusCodes['api_error'],
                'errors': 'Invalid credentials',
                'results': None
            }),400

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

    hashed_password = encrypt_password(password)

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
        user_id = insert_person(cur, {
            'username': data.get('username'),
            'email': data.get('email'),
            'password': hashed_password,
            'date_of_birth': date_of_birth
        })

        cur.execute("""
            INSERT INTO student (person_id, district)
            VALUES (%s, %s)
        """, (user_id, district))
        
        conn.commit()
        
        return flask.jsonify({
                    'status': StatusCodes['success'],
                    'errors': None,
                    'results': user_id
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

    hashed_password = encrypt_password(password)

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
        user_id = insert_person(cur, {
            'username': data.get('username'),
            'email': data.get('email'),
            'password': hashed_password,
            'date_of_birth': date_of_birth
        })
        
        cur.execute("""INSERT INTO employee (person_id,hire_date,salary,status)
                    VALUES (%s, %s, %s, %s) 
                    """,(user_id, hire_date, salary, status))

        cur.execute("""
                    INSERT INTO staff (person_id, roll) VALUES (%s, %s)
                    VALUES (%s,%s)""",(user_id,roll))

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

    hashed_password = encrypt_password(password)

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
        user_id = insert_person(cur, {
            'username': data.get('username'),
            'email': data.get('email'),
            'password': hashed_password,
            'date_of_birth': date_of_birth
        })

        cur.execute("""INSERT INTO employee (person_id,hire_date,salary,status)
                    VALUES (%s, %s, %s, %s) 
                    """,(user_id, hire_date, salary, status))

        cur.execute("""
                    INSERT INTO instructor (person_id)
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
        logger.error(f'POST /dbproj/register/instructor - erro: {error}')
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
        
        cur.execute("""
            INSERT INTO degree_enrollment(student_id, degree_id, enrollment_date, status)
            VALUES (%s, %s, %s, 'Active')"""
        ,(person_id,degree_id, date,))
        
        conn.commit()
        
        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None,
            'results': None
            }),200
    
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
    
    person_id_json = data.get('student_id')
    person_id_token = flask.g.user['user_id']

    date_str = data.get('date')

    if not person_id_json or not date_str:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Student ID and date are required',
            'results': None
    }), 400

    if int(person_id_json) != int(person_id_token):
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Acess denied: You can only enroll yourself.',
            'results': None
        }), 403
    
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
        
        cur.execute(
            """
            INSERT INTO activity_enrollment (student_id,activity_id,enrollment_date)
            VALUES (%s, %s, %s)"""
            ,(person_id, activity_id, date))
        
        conn.commit()
        
        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None,
            'results': None
        }),200
    
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
    
    student_id = flask.g.user["user_id"]
    data = flask.request.get_json()
    classes = data.get('classes', []) 
    
    
    enrollment_date = datetime.date.today()

    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None}), 500

    try:
        cur = conn.cursor()
        
        cur.execute("CALL enroll_student_course_edition(%s, %s, %s, %s)", 
                    (student_id, course_edition_id, classes, enrollment_date))
        
        conn.commit()
        
        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None
        }), 200

    except psycopg2.errors.RaiseException as error:
        conn.rollback()
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': str(error).strip(), 
        }), 400
        
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
        }), 500
    finally:
        if conn is not None:
            conn.close()

@app.route('/dbproj/submit_grades/<course_edition_id>', methods=['POST'])
@token_required
@roles_required('instructor')
def submite_grade(course_edition_id):

    intructor_id = flask.g.user["user_id"]

    data = flask.request.get_json()
    period = data.get('period')
    grades = data.get('grades', [])

    if not period or not grades:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Period and grades are required',
            'results': None
        }), 400

    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None}), 500

    try:
        cur = conn.cursor()

        cur.execute("""
        SELECT evaluation_period
        FROM course_edition
        WHERE edition_id = %s AND coordinator_id = %s""",
        (course_edition_id, intructor_id))

        edition = cur.fetchone()

        if not edition:
            return flask.jsonify({
                'status': StatusCodes['api_error'],
                'errors': 'Course edition not found or you are not the coordinator',
            }), 403
                
        if edition[0] != period:
            return flask.jsonify({
                'status': StatusCodes['api_error'],
                'errors': 'Invalid evaluation period for this course edition.'
            }), 400

        # 2. Grades
        for student_grade in grades:
            student_id = student_grade[0]
            grade = float(student_grade[1])
            
            is_approved = grade >= 9.5 

            cur.execute("""
                UPDATE course_enrollment
                SET grade = %s, approved = %s
                WHERE student_id = %s AND edition_id = %s
            """, (grade, is_approved, student_id, course_edition_id))

        conn.commit()

        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None
        }), 200

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error)
        }), 500
    finally:
        if conn is not None:
            conn.close()


@app.route('/dbproj/student_details/<person_id>', methods=['GET'])
@token_required
@roles_required('staff','student')
def student_details(person_id):
    
    user_role = flask.g.user.get("role")
    user_id = flask.g.user["user_id"]

    if user_role == 'student' and str(user_id) != str(person_id):
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'errors': 'Access denied: You can only view your own details.',
            'results': None
        }), 403
    
    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None})

    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT
                ce.edition_id AS course_edition_id,
                c.course_name,
                ce.edition_year,
                cen.grade
            FROM course_enrollment cen
            JOIN course_edition ce ON cen.edition_id = ce.edition_id
            JOIN course c on ce.course_id = c.course_id
            WHERE cen.student_id = %s
            ORDER BY ce.edition_year DESC
        """, (person_id,))

        rows = cur.fetchall()

        results = []
        for r in rows:
            results.append({
                "course_edition_id": r[0],
                "course_name": r[1],
                "course_edition_year": r[2],
                "grade": float(r[3]) if r[3] is not None else None
            })

        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None,
            'results': results
        })
    
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/student_details/{person_id} - erro: {error}')
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        }),500
        
    finally:
        if conn is not None:
            conn.close()


@app.route('/dbproj/degree_details/<degree_id>', methods=['GET'])
@token_required
@roles_required('staff')
def degree_details(degree_id):
    
    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None})

    try:
        cur = conn.cursor()
        
    
        cur.execute("""
            SELECT 
                c.course_id,
                c.name AS course_name,
                ce.edition_id AS course_edition_id,
                ce.edition_year AS course_edition_year,
                ce.capacity,
                COUNT(cen.student_id) AS enrolled_count,
                COUNT(cen.student_id) FILTER (WHERE cen.approved = TRUE) AS approved_count,
                ce.coordinator_id,
                (
                    -- Subquery to group assistent instructors without messing up the student counts!
                    SELECT COALESCE(ARRAY_AGG(instructor_id), ARRAY[]::INT[])
                    FROM edition_instructor ei
                    WHERE ei.edition_id = ce.edition_id
                ) AS instructors
            FROM degree_course dc
            JOIN course c ON dc.course_id = c.course_id
            JOIN course_edition ce ON c.course_id = ce.course_id
            LEFT JOIN course_enrollment cen ON ce.edition_id = cen.edition_id
            WHERE dc.degree_id = %s
            GROUP BY 
                c.course_id, 
                c.name, 
                ce.edition_id, 
                ce.edition_year, 
                ce.capacity, 
                ce.coordinator_id
            ORDER BY ce.edition_year DESC;
        """, (degree_id,))

        rows = cur.fetchall()

        results = []
        for r in rows:
            results.append({
                "course_id": r[0],
                "course_name": r[1],
                "course_edition_id": r[2],
                "course_edition_year": r[3],
                "capacity": r[4],
                "enrolled_count": r[5],
                "approved_count": r[6],
                "coordinator_id": r[7],
                "instructors": r[8] if r[8] is not None else []
            })

        return flask.jsonify({
            "status": StatusCodes["success"],
            "errors": None,
            "results": results
        })
    
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/degree_details/{degree_id} - erro: {error}')
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        })
        
    finally:
        if conn is not None:
            conn.close()
    

@app.route('/dbproj/top3', methods=['GET'])
@token_required
@roles_required('staff')
def top3_students():
    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None}), 500

    try:
        cur = conn.cursor()
        
        cur.execute("""
            WITH top_students AS (
                SELECT 
                    cen.student_id,
                    p.name AS student_name,
                    ROUND(AVG(cen.grade), 2) AS average_grade
                FROM course_enrollment cen
                JOIN course_edition ce ON cen.edition_id = ce.edition_id
                JOIN person p ON p.id = cen.student_id
                WHERE ce.edition_year = EXTRACT(YEAR FROM CURRENT_DATE)
                  AND cen.grade IS NOT NULL
                GROUP BY cen.student_id, p.name
                ORDER BY average_grade DESC
                LIMIT 3
            )
            SELECT 
                ts.student_name,
                ts.average_grade,
                (
                    SELECT COALESCE(json_agg(json_build_object(
                        'course_edition_id', ce.edition_id,
                        'course_edition_name', c.name,
                        'grade', cen2.grade,
                        'date', cen2.enrollment_date
                    )), '[]'::json)
                    FROM course_enrollment cen2
                    JOIN course_edition ce ON cen2.edition_id = ce.edition_id
                    JOIN course c ON ce.course_id = c.course_id
                    WHERE cen2.student_id = ts.student_id
                ) AS grades,
                (
                    SELECT COALESCE(json_agg(a.name), '[]'::json)
                    FROM activity_enrollment ae
                    JOIN activity a ON ae.activity_id = a.id
                    WHERE ae.student_id = ts.student_id
                ) AS activities
            FROM top_students ts
            ORDER BY ts.average_grade DESC;
        """)
        
        rows = cur.fetchall()
        
        results = []
        for r in rows:
            results.append({
                "student_name": r[0],
                "average_grade": float(r[1]),
                # The database already returns a fully formatted Python list/dictionary here!
                "grades": r[2], 
                "activities": r[3] 
            })
            
        return flask.jsonify({
            "status": StatusCodes['success'],
            "errors": None,
            "results": results
        }), 200

    except (Exception, psycopg2.DatabaseError) as error:
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        }), 500
    finally:
        if conn is not None:
            conn.close()
  

@app.route('/dbproj/top_by_district/', methods=['GET'])
@token_required
@roles_required('staff')
def top_by_district():
    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None}), 500

    try:
        cur = conn.cursor()
        
        # Using a Window Function (RANK) to find the top student per district
        cur.execute("""
            WITH student_averages AS (
                SELECT 
                    p.id AS student_id,
                    p.district,
                    ROUND(AVG(cen.grade), 2) AS average_grade
                FROM person p
                JOIN course_enrollment cen ON p.id = cen.student_id
                WHERE cen.grade IS NOT NULL
                GROUP BY p.id, p.district
            ),
            ranked_students AS (
                SELECT 
                    student_id,
                    district,
                    average_grade,
                    RANK() OVER (PARTITION BY district ORDER BY average_grade DESC) as rank
                FROM student_averages
            )
            SELECT student_id, district, average_grade
            FROM ranked_students
            WHERE rank = 1;
        """)
        
        rows = cur.fetchall()
        
        results = []
        for r in rows:
            results.append({
                "student_id": r[0],
                "district": r[1],
                "average_grade": float(r[2])
            })
            
        return flask.jsonify({
            "status": StatusCodes['success'],
            "errors": None,
            "results": results
        }), 200

    except (Exception, psycopg2.DatabaseError) as error:
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        }), 500
    finally:
        if conn is not None:
            conn.close()


@app.route('/dbproj/report', methods=['GET'])
@token_required
@roles_required('staff')
def monthly_report():
    conn = db_connection()
    if conn is None:
        return flask.jsonify({'status': StatusCodes['internal_error'], 'errors': 'Database connection error', 'results': None}), 500

    try:
        cur = conn.cursor()
        
        # 1 query using CTEs and Window Functions (RANK)
        cur.execute("""
            WITH monthly_stats AS (
                SELECT 
                    TO_CHAR(cen.enrollment_date, 'YYYY-MM') AS month,
                    ce.edition_id AS course_edition_id,
                    c.name AS course_edition_name,
                    COUNT(cen.student_id) FILTER (WHERE cen.approved = TRUE) AS count_approved,
                    COUNT(cen.student_id) AS count_evaluated
                FROM course_enrollment cen
                JOIN course_edition ce ON cen.edition_id = ce.edition_id
                JOIN course c ON ce.course_id = c.course_id
                WHERE cen.enrollment_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '12 months'
                GROUP BY 
                    TO_CHAR(cen.enrollment_date, 'YYYY-MM'), 
                    ce.edition_id, 
                    c.name
            ),
            ranked_stats AS (
                SELECT 
                    month,
                    course_edition_id,
                    course_edition_name,
                    count_approved,
                    count_evaluated,
                    RANK() OVER (PARTITION BY month ORDER BY count_approved DESC) as rank
                FROM monthly_stats
            )
            SELECT 
                month,
                course_edition_id,
                course_edition_name,
                count_approved,
                count_evaluated
            FROM ranked_stats
            WHERE rank = 1
            ORDER BY month DESC;
        """)
        
        rows = cur.fetchall()
        
        results = []
        for r in rows:
            results.append({
                "month": r[0],
                "course_edition_id": r[1],
                "course_edition_name": r[2],
                "approved": r[3],
                "evaluated": r[4]
            })
            
        return flask.jsonify({
            "status": StatusCodes['success'],
            "errors": None,
            "results": results
        }), 200

    except (Exception, psycopg2.DatabaseError) as error:
        return flask.jsonify({
            'status': StatusCodes['internal_error'],
            'errors': str(error),
            'results': None
        }), 500
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

        # 1. Check if the student exists and is of type 'student'
        cur.execute("""
            SELECT person_id FROM student 
            WHERE person_id = %s
        """, (person_id,))
        
        if not cur.fetchone():
            return flask.jsonify({
                'status': StatusCodes['api_error'],
                'errors': 'Student not found or not a valid student ID'
            }), 404
        
        cur.execute("DELETE FROM class_enrollment WHERE student_id = %s", (person_id,))

        cur.execute("DELETE FROM course_enrollment WHERE student_id = %s", (person_id,))

        cur.execute("DELETE FROM activity_enrollment WHERE student_id = %s", (person_id,))

        cur.execute("DELETE FROM degree_enrollment WHERE student_id = %s", (person_id,))

        cur.execute("DELETE FROM student WHERE person_id = %s", (person_id,))

        cur.execute("DELETE FROM person WHERE id = %s", (person_id,))

        
        conn.commit()
        
        return flask.jsonify({
            'status': StatusCodes['success'],
            'errors': None,
            'results': "Student eliminated!"
        }), 200
        
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
