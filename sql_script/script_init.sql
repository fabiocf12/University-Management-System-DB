CREATE TABLE student (
	student_id SERIAL NOT NULL,
	district	 VARCHAR(100) NOT NULL,
	person_id	 INTEGER,
	PRIMARY KEY(person_id)
);

CREATE TABLE instructor (
	employee_person_id INTEGER,
	PRIMARY KEY(employee_person_id)
);

CREATE TABLE degree (
	degree_id	 SERIAL,
	degree_name	 VARCHAR(100) NOT NULL,
	credits	 INTEGER NOT NULL,
	months_duration INTEGER NOT NULL,
	tuition	 FLOAT(8) NOT NULL,
	PRIMARY KEY(degree_id)
);

CREATE TABLE course (
	course_id	 SERIAL,
	course_name VARCHAR(512) NOT NULL,
	credits	 INTEGER NOT NULL,
	PRIMARY KEY(course_id)
);

CREATE TABLE courseedition (
	edition_id			 SERIAL,
	edition_year			 INTEGER NOT NULL,
	capacity			 INTEGER NOT NULL,
	edition_semester		 INTEGER NOT NULL,
	instructor_employee_person_id INTEGER NOT NULL,
	course_course_id		 INTEGER NOT NULL,
	PRIMARY KEY(edition_id)
);

CREATE TABLE classroom (
	classroom_id	 SERIAL,
	campus_building VARCHAR(100) NOT NULL,
	room_number	 INTEGER NOT NULL,
	capacity	 INTEGER NOT NULL,
	PRIMARY KEY(classroom_id)
);

CREATE TABLE financialaccount (
	tuition_charges	 FLOAT(8) NOT NULL,
	fees_charges	 FLOAT(8) NOT NULL,
	other_charges	 FLOAT(8) NOT NULL,
	student_person_id INTEGER,
	PRIMARY KEY(student_person_id)
);

CREATE TABLE extraactivity (
	activity_id	 SERIAL,
	name		 VARCHAR(100) NOT NULL,
	fee		 FLOAT(8) NOT NULL,
	description	 VARCHAR(100) NOT NULL,
	months_duration INTEGER NOT NULL,
	PRIMARY KEY(activity_id)
);

CREATE TABLE person (
	id		 SERIAL,
	name		 VARCHAR(100) NOT NULL,
	password   VARCHAR(512) NOT NULL,
	email	 VARCHAR(100) NOT NULL,
	date_of_birth DATE NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE staff (
	roll		 VARCHAR(100) NOT NULL,
	employee_person_id INTEGER,
	PRIMARY KEY(employee_person_id)
);

CREATE TABLE class (
	id			 SERIAL NOT NULL,
	type			 VARCHAR(100) NOT NULL,
	start_schedule		 TIMESTAMP NOT NULL,
	subject			 VARCHAR(100) NOT NULL,
	courseedition_edition_id INTEGER NOT NULL,
	classroom_classroom_id	 INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE attendance (
	attendance_id	 SERIAL,
	present		 BOOL NOT NULL,
	class_id		 INTEGER NOT NULL,
	student_person_id INTEGER NOT NULL,
	PRIMARY KEY(attendance_id)
);

CREATE TABLE enrollment (
	enrollment_id	 SERIAL,
	enrollment_date_	 DATE NOT NULL,
	status		 BOOL NOT NULL,
	student_person_id INTEGER NOT NULL,
	PRIMARY KEY(enrollment_id)
);

CREATE TABLE course_enrollment (
	grade			 FLOAT(8) NOT NULL,
	approved		 BOOL NOT NULL,
	courseedition_edition_id INTEGER NOT NULL,
	enrollment_enrollment_id INTEGER,
	PRIMARY KEY(enrollment_enrollment_id)
);

CREATE TABLE degree_enrollment (
	average_grade		 FLOAT(8) NOT NULL,
	approved_courses_count	 INTEGER NOT NULL,
	degree_degree_id	 INTEGER NOT NULL,
	enrollment_enrollment_id INTEGER,
	PRIMARY KEY(enrollment_enrollment_id)
);

CREATE TABLE extraactivity_enrollment (
	extraactivity_activity_id INTEGER NOT NULL,
	enrollment_enrollment_id	 INTEGER,
	PRIMARY KEY(enrollment_enrollment_id)
);

CREATE TABLE employee (
	employee_id SERIAL NOT NULL,
	hire_date	 DATE NOT NULL,
	salary	 FLOAT(8) NOT NULL,
	status	 VARCHAR(100) NOT NULL,
	person_id	 INTEGER,
	PRIMARY KEY(person_id)
);

CREATE TABLE class_enrollment (
	class_enrollment_id_ SERIAL,
	class_id		 INTEGER NOT NULL,
	PRIMARY KEY(class_enrollment_id_)
);

CREATE TABLE course_enrollment_class_enrollment (
	course_enrollment_enrollment_enrollment_id INTEGER,
	class_enrollment_class_enrollment_id_	 INTEGER,
	PRIMARY KEY(course_enrollment_enrollment_enrollment_id,class_enrollment_class_enrollment_id_)
);

CREATE TABLE student_courseedition (
	student_person_id	 INTEGER,
	courseedition_edition_id INTEGER,
	PRIMARY KEY(student_person_id,courseedition_edition_id)
);

CREATE TABLE student_class (
	student_person_id INTEGER,
	class_id		 INTEGER,
	PRIMARY KEY(student_person_id,class_id)
);

CREATE TABLE extraactivity_student (
	extraactivity_activity_id INTEGER,
	student_person_id	 INTEGER,
	PRIMARY KEY(extraactivity_activity_id,student_person_id)
);

CREATE TABLE student_degree (
	student_person_id INTEGER,
	degree_degree_id	 INTEGER,
	PRIMARY KEY(student_person_id,degree_degree_id)
);

CREATE TABLE degree_course (
	degree_degree_id INTEGER,
	course_course_id INTEGER,
	PRIMARY KEY(degree_degree_id,course_course_id)
);

CREATE TABLE courseedition_instructor (
	courseedition_edition_id	 INTEGER,
	instructor_employee_person_id INTEGER,
	PRIMARY KEY(courseedition_edition_id,instructor_employee_person_id)
);

CREATE TABLE course_course (
	course_course_id	 INTEGER,
	course_course_id1 INTEGER,
	PRIMARY KEY(course_course_id,course_course_id1)
);

ALTER TABLE student ADD UNIQUE (student_id);
ALTER TABLE student ADD CONSTRAINT student_fk1 FOREIGN KEY (person_id) REFERENCES person(id);
ALTER TABLE instructor ADD CONSTRAINT instructor_fk1 FOREIGN KEY (employee_person_id) REFERENCES employee(person_id);
ALTER TABLE courseedition ADD CONSTRAINT courseedition_fk1 FOREIGN KEY (instructor_employee_person_id) REFERENCES instructor(employee_person_id);
ALTER TABLE courseedition ADD CONSTRAINT courseedition_fk2 FOREIGN KEY (course_course_id) REFERENCES course(course_id);
ALTER TABLE classroom ADD UNIQUE (room_number);
ALTER TABLE financialaccount ADD CONSTRAINT financialaccount_fk1 FOREIGN KEY (student_person_id) REFERENCES student(person_id);
ALTER TABLE person ADD UNIQUE (email);
ALTER TABLE staff ADD CONSTRAINT staff_fk1 FOREIGN KEY (employee_person_id) REFERENCES employee(person_id);
ALTER TABLE class ADD CONSTRAINT class_fk1 FOREIGN KEY (courseedition_edition_id) REFERENCES courseedition(edition_id);
ALTER TABLE class ADD CONSTRAINT class_fk2 FOREIGN KEY (classroom_classroom_id) REFERENCES classroom(classroom_id);
ALTER TABLE attendance ADD CONSTRAINT attendance_fk1 FOREIGN KEY (class_id) REFERENCES class(id);
ALTER TABLE attendance ADD CONSTRAINT attendance_fk2 FOREIGN KEY (student_person_id) REFERENCES student(person_id);
ALTER TABLE enrollment ADD CONSTRAINT enrollment_fk1 FOREIGN KEY (student_person_id) REFERENCES student(person_id);
ALTER TABLE course_enrollment ADD CONSTRAINT course_enrollment_fk1 FOREIGN KEY (courseedition_edition_id) REFERENCES courseedition(edition_id);
ALTER TABLE course_enrollment ADD CONSTRAINT course_enrollment_fk2 FOREIGN KEY (enrollment_enrollment_id) REFERENCES enrollment(enrollment_id);
ALTER TABLE degree_enrollment ADD CONSTRAINT degree_enrollment_fk1 FOREIGN KEY (degree_degree_id) REFERENCES degree(degree_id);
ALTER TABLE degree_enrollment ADD CONSTRAINT degree_enrollment_fk2 FOREIGN KEY (enrollment_enrollment_id) REFERENCES enrollment(enrollment_id);
ALTER TABLE extraactivity_enrollment ADD CONSTRAINT extraactivity_enrollment_fk1 FOREIGN KEY (extraactivity_activity_id) REFERENCES extraactivity(activity_id);
ALTER TABLE extraactivity_enrollment ADD CONSTRAINT extraactivity_enrollment_fk2 FOREIGN KEY (enrollment_enrollment_id) REFERENCES enrollment(enrollment_id);
ALTER TABLE employee ADD UNIQUE (employee_id);
ALTER TABLE employee ADD CONSTRAINT employee_fk1 FOREIGN KEY (person_id) REFERENCES person(id);
ALTER TABLE class_enrollment ADD CONSTRAINT class_enrollment_fk1 FOREIGN KEY (class_id) REFERENCES class(id);
ALTER TABLE course_enrollment_class_enrollment ADD CONSTRAINT course_enrollment_class_enrollment_fk1 FOREIGN KEY (course_enrollment_enrollment_enrollment_id) REFERENCES course_enrollment(enrollment_enrollment_id);
ALTER TABLE course_enrollment_class_enrollment ADD CONSTRAINT course_enrollment_class_enrollment_fk2 FOREIGN KEY (class_enrollment_class_enrollment_id_) REFERENCES class_enrollment(class_enrollment_id_);
ALTER TABLE student_courseedition ADD CONSTRAINT student_courseedition_fk1 FOREIGN KEY (student_person_id) REFERENCES student(person_id);
ALTER TABLE student_courseedition ADD CONSTRAINT student_courseedition_fk2 FOREIGN KEY (courseedition_edition_id) REFERENCES courseedition(edition_id);
ALTER TABLE student_class ADD CONSTRAINT student_class_fk1 FOREIGN KEY (student_person_id) REFERENCES student(person_id);
ALTER TABLE student_class ADD CONSTRAINT student_class_fk2 FOREIGN KEY (class_id) REFERENCES class(id);
ALTER TABLE extraactivity_student ADD CONSTRAINT extraactivity_student_fk1 FOREIGN KEY (extraactivity_activity_id) REFERENCES extraactivity(activity_id);
ALTER TABLE extraactivity_student ADD CONSTRAINT extraactivity_student_fk2 FOREIGN KEY (student_person_id) REFERENCES student(person_id);
ALTER TABLE student_degree ADD CONSTRAINT student_degree_fk1 FOREIGN KEY (student_person_id) REFERENCES student(person_id);
ALTER TABLE student_degree ADD CONSTRAINT student_degree_fk2 FOREIGN KEY (degree_degree_id) REFERENCES degree(degree_id);
ALTER TABLE degree_course ADD CONSTRAINT degree_course_fk1 FOREIGN KEY (degree_degree_id) REFERENCES degree(degree_id);
ALTER TABLE degree_course ADD CONSTRAINT degree_course_fk2 FOREIGN KEY (course_course_id) REFERENCES course(course_id);
ALTER TABLE courseedition_instructor ADD CONSTRAINT courseedition_instructor_fk1 FOREIGN KEY (courseedition_edition_id) REFERENCES courseedition(edition_id);
ALTER TABLE courseedition_instructor ADD CONSTRAINT courseedition_instructor_fk2 FOREIGN KEY (instructor_employee_person_id) REFERENCES instructor(employee_person_id);
ALTER TABLE course_course ADD CONSTRAINT course_course_fk1 FOREIGN KEY (course_course_id) REFERENCES course(course_id);
ALTER TABLE course_course ADD CONSTRAINT course_course_fk2 FOREIGN KEY (course_course_id1) REFERENCES course(course_id);


-- ADMIN DEFAULT USER
INSERT INTO person (id, name,password, email, date_of_birth)
VALUES (1,'admin','1234','admin@uni.pt',CURRENT_DATE);

INSERT INTO employee (hire_date, salary, status, person_id)
VALUES (CURRENT_DATE,2000,'active',1);

INSERT INTO staff (roll, employee_person_id)
VALUES ('administrator', 1);

SELECT setval('person_id_seq', (SELECT MAX(id) FROM person));
