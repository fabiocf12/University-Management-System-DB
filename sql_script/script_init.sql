


DROP TABLE IF EXISTS person, student, employee, staff, instructor, degree, course, course_prerequisite, degree_course, course_edition, classroom, class, attendance, extra_activity, degree_enrollment, course_enrollment, class_enrollment, activity_enrollment CASCADE;

CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    password VARCHAR(512) NOT NULL
);

CREATE TABLE degree (
    degree_id SERIAL PRIMARY KEY,
    degree_name VARCHAR(100) NOT NULL,
    credits INTEGER NOT NULL,
    months_duration INTEGER NOT NULL,
    tuition FLOAT NOT NULL
);

CREATE TABLE course (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(512) NOT NULL,
    credits INTEGER NOT NULL
);

CREATE TABLE classroom (
    classroom_id SERIAL PRIMARY KEY,
    campus_building VARCHAR(100) NOT NULL,
    room_number INTEGER UNIQUE NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE extra_activity (
    activity_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(100) NOT NULL,
    fee FLOAT NOT NULL,
    months_duration INTEGER NOT NULL
);


CREATE TABLE student (
    person_id INTEGER PRIMARY KEY REFERENCES person(id),
    district VARCHAR(100) NOT NULL,
    tuition_charges FLOAT NOT NULL DEFAULT 0,
    fees_charges FLOAT NOT NULL DEFAULT 0,
    other_charges FLOAT NOT NULL DEFAULT 0
);

CREATE TABLE employee (
    person_id INTEGER PRIMARY KEY REFERENCES person(id),
    hire_date DATE NOT NULL,
    salary FLOAT NOT NULL,
    status VARCHAR(100) NOT NULL
);

CREATE TABLE staff (
    person_id INTEGER PRIMARY KEY REFERENCES employee(person_id),
    roll VARCHAR(100) NOT NULL
);

CREATE TABLE instructor (
    person_id INTEGER PRIMARY KEY REFERENCES employee(person_id)
);


CREATE TABLE course_prerequisite (
    course_id INTEGER REFERENCES course(course_id),
    prerequisite_id INTEGER REFERENCES course(course_id),
    PRIMARY KEY (course_id, prerequisite_id)
);

CREATE TABLE degree_course (
    degree_id INTEGER REFERENCES degree(degree_id),
    course_id INTEGER REFERENCES course(course_id),
    PRIMARY KEY (degree_id, course_id)
);

CREATE TABLE course_edition (
    edition_id SERIAL PRIMARY KEY,
    edition_year INTEGER NOT NULL,
    edition_semester INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    evaluation_period VARCHAR(100) NOT NULL,
    course_id INTEGER NOT NULL REFERENCES course(course_id),
    coordinator_id INTEGER NOT NULL REFERENCES instructor(person_id)
);

CREATE TABLE class (
    class_id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    start_schedule TIMESTAMP NOT NULL,
    subject VARCHAR(100) NOT NULL,
    edition_id INTEGER NOT NULL REFERENCES course_edition(edition_id),
    classroom_id INTEGER NOT NULL REFERENCES classroom(classroom_id)
);


CREATE TABLE degree_enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(person_id),
    degree_id INTEGER NOT NULL REFERENCES degree(degree_id),
    enrollment_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active'
);

CREATE TABLE course_enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(person_id),
    edition_id INTEGER NOT NULL REFERENCES course_edition(edition_id),
    enrollment_date DATE NOT NULL,
    grade FLOAT,
    approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE class_enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(person_id),
    class_id INTEGER NOT NULL REFERENCES class(class_id)
);

CREATE TABLE activity_enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(person_id),
    activity_id INTEGER NOT NULL REFERENCES extra_activity(activity_id),
    enrollment_date DATE NOT NULL
);

CREATE TABLE attendance (
    attendance_id SERIAL PRIMARY KEY,
    present BOOLEAN NOT NULL DEFAULT FALSE,
    student_id INTEGER NOT NULL REFERENCES student(person_id),
    class_id INTEGER NOT NULL REFERENCES class(class_id)
);



CREATE OR REPLACE FUNCTION update_tuition_charges()
RETURNS TRIGGER AS $$
DECLARE
    v_tuition FLOAT;
BEGIN
    -- New insertion
    IF TG_OP = 'INSERT' THEN
        SELECT tuition INTO v_tuition FROM degree WHERE degree_id = NEW.degree_id;
        UPDATE student 
        SET tuition_charges = tuition_charges + v_tuition 
        WHERE person_id = NEW.student_id;
        RETURN NEW;
        
    -- If deleting
    ELSIF TG_OP = 'DELETE' THEN
        SELECT tuition INTO v_tuition FROM degree WHERE degree_id = OLD.degree_id;
        UPDATE student 
        SET tuition_charges = tuition_charges - v_tuition 
        WHERE person_id = OLD.student_id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_degree_enrollment_finance
AFTER INSERT OR DELETE ON degree_enrollment
FOR EACH ROW EXECUTE FUNCTION update_tuition_charges();




CREATE OR REPLACE FUNCTION update_fee_charges()
RETURNS TRIGGER AS $$
DECLARE
    v_fee FLOAT;
BEGIN
    -- New insertion
    IF TG_OP = 'INSERT' THEN
        SELECT fee INTO v_fee FROM extra_activity WHERE activity_id = NEW.activity_id;
        UPDATE student 
        SET fees_charges = fees_charges + v_fee 
        WHERE person_id = NEW.student_id;
        RETURN NEW;
        
    -- If deleting
    ELSIF TG_OP = 'DELETE' THEN
        SELECT fee INTO v_fee FROM extra_activity WHERE activity_id = OLD.activity_id;
        UPDATE student 
        SET fees_charges = fees_charges - v_fee 
        WHERE person_id = OLD.student_id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_extra_activity_enrollment_finance
AFTER INSERT OR DELETE ON activity_enrollment
FOR EACH ROW EXECUTE FUNCTION update_fee_charges();


CREATE OR REPLACE PROCEDURE enroll_student_course_edition(
    p_student_id INT,
    p_edition_id INT,
    p_classes INT[],
    p_date DATE
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_course_id INT;
    v_capacity INT;
    v_enrolled_count INT;
    v_missing_prereq INT;
    v_valid_degree BOOLEAN;
    v_class_id INT;
BEGIN
    -- 1. Get course_id and capacity of this edition
    SELECT course_id, capacity INTO v_course_id, v_capacity
    FROM course_edition
    WHERE edition_id = p_edition_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Course edition not found.';
    END IF;

    -- 2.  Check if the course belongs to the student's degree
    SELECT EXISTS (
        SELECT 1 FROM degree_enrollment de
        JOIN degree_course dc ON de.degree_id = dc.degree_id
        WHERE de.student_id = p_student_id AND dc.course_id = v_course_id AND de.status = 'Active'
    ) INTO v_valid_degree;

    IF NOT v_valid_degree THEN
        RAISE EXCEPTION 'Student is not enrolled in a degree that includes this course.';
    END IF;

    -- 3. Check prerequisites
    SELECT cp.prerequisite_id INTO v_missing_prereq
    FROM course_prerequisite cp
    LEFT JOIN (
        SELECT ce_inner.course_id 
        FROM course_enrollment c_enr
        JOIN course_edition ce_inner ON c_enr.edition_id = ce_inner.edition_id
        WHERE c_enr.student_id = p_student_id AND c_enr.approved = TRUE
    ) passed_courses ON cp.prerequisite_id = passed_courses.course_id
    WHERE cp.course_id = v_course_id AND passed_courses.course_id IS NULL
    LIMIT 1;

    IF v_missing_prereq IS NOT NULL THEN
        RAISE EXCEPTION 'Student has not passed all prerequisites.';
    END IF;

    -- 4. Check capacity
    SELECT COUNT(*) INTO v_enrolled_count
    FROM course_enrollment
    WHERE edition_id = p_edition_id;

    IF v_enrolled_count >= v_capacity THEN
        RAISE EXCEPTION 'Course edition is at full capacity.';
    END IF;

    -- 5. Insert in course edition
    INSERT INTO course_enrollment (student_id, edition_id, enrollment_date)
    VALUES (p_student_id, p_edition_id, p_date);

    -- 6. Iterate classes array and enroll student in each one
    FOREACH v_class_id IN ARRAY p_classes
    LOOP
        INSERT INTO class_enrollment (student_id, class_id)
        VALUES (p_student_id, v_class_id);
    END LOOP;
    
END;
$$;

WITH new_person AS (
    INSERT INTO person (name, email, date_of_birth, password) 
    VALUES ('Admin Principal', 'admin@uni.pt', '1980-01-01', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9')
    RETURNING id
),

new_employee AS (
    INSERT INTO employee (person_id, hire_date, salary, status)
    SELECT id, CURRENT_DATE, 12000, 'Active'
    FROM new_person
    RETURNING person_id
)

INSERT INTO staff (person_id,roll) 
SELECT person_id, 'staff'
FROM new_employee;

--
INSERT INTO person (name, email, date_of_birth, password) 
VALUES ('Prof Coordenador', 'prof@uni.pt', '1980-01-01', '00624b02e1f9b996a3278f559d5d55313552ad2c0bafc82adfd975c12df61eaf');

INSERT INTO employee (person_id,hire_date,salary,status) VALUES (2,CURRENT_DATE,3200,'Active');
INSERT INTO instructor (person_id) VALUES (2);

-- 1. Degrees
INSERT INTO degree (degree_id, degree_name, credits, months_duration, tuition) VALUES (1, 'Engenharia Informática',180, 36, 3000);

-- 2. Courses
INSERT INTO course (course_id, course_name,credits) VALUES (1, 'Bases de Dados',6);
INSERT INTO course (course_id, course_name,credits) VALUES (2, 'Machine Learning',5);

-- 3. Link Degree to Course
INSERT INTO degree_course (degree_id, course_id) VALUES (1, 1);
INSERT INTO degree_course (degree_id, course_id) VALUES (1, 2);

-- 4. Extracurricular Activities
INSERT INTO extra_activity (activity_id, name,description,fee,months_duration) VALUES (1, 'Gym - Weight Training','Stay Hard!',100,6);
INSERT INTO extra_activity (activity_id, name,description,fee,months_duration)  VALUES (2, 'Competitive Programming Club','Stay hard!',75,3);

-- 5. Classrooms (Required by the Annex A description)
INSERT INTO classroom (classroom_id, campus_building, room_number, capacity) VALUES (1, 'A03', 34, 50);
INSERT INTO classroom (classroom_id, campus_building, room_number, capacity) VALUES (2, 'A02', 17, 30);

-- 6. Course Edition (Requires coordinator_id = 3)
INSERT INTO course_edition (edition_id, edition_year, edition_semester, capacity, evaluation_period, course_id, coordinator_id)
VALUES (1, 2026, 2, 150, 'Epoca Normal', 1, 2);

-- 7. Classes for Edition 1 (Theory and Practical Lab, linking to classrooms)
INSERT INTO class (class_id,type,start_schedule,subject,edition_id,classroom_id)
VALUES (1,'T',CURRENT_DATE, 'Microbiologia',1,1);

INSERT INTO class (class_id,type,start_schedule,subject,edition_id,classroom_id)
VALUES (2,'P',CURRENT_DATE, 'Anatomia II',1,2);
