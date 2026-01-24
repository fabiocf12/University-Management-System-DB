-- ---------------------------------------------------
-- 1. Degrees
-- ---------------------------------------------------
INSERT INTO degree (degree_id, degree_name, credits, months_duration, tuition) VALUES
(1, 'Computer Science', 180, 36, 12000),
(2, 'Mathematics', 180, 36, 11000),
(3, 'Physics', 180, 36, 11500);

-- ---------------------------------------------------
-- 2. Activities
-- ---------------------------------------------------
INSERT INTO extraactivity (activity_id, name, fee, description, months_duration) VALUES
(1, 'Robotics Club', 100, 'Extracurricular robotics activities', 12),
(2, 'Math Olympiad', 50, 'Competitive math training', 6),
(3, 'Physics Lab Workshop', 80, 'Hands-on physics experiments', 3);


-- ---------------------------------------------------
-- 3. Course editions
-- ---------------------------------------------------

INSERT INTO course (course_id, course_name,credits) VALUES
(101, 'Intro to CS',6),
(102, 'Advanced Math',6),
(103, 'Physics I',6);

INSERT INTO courseedition (edition_id, edition_year, course_course_id, capacity, edition_semester,instructor_employee_person_id) VALUES
(1, 2025, 101, 50, 1,14),
(2, 2025, 102, 40, 1,14),
(3, 2025, 103, 60, 2,14);


-- ---------------------------------------------------
-- Classroom
-- ---------------------------------------------------

INSERT INTO classroom (classroom_id, campus_building, room_number, capacity) VALUES
(1, 'Polo II', 1, 40),
(2, 'Polo II', 2, 30),
(3, 'Polo I', 10, 50),
(4, 'Polo I', 5, 25);

-- ---------------------------------------------------
-- Classes
-- ---------------------------------------------------

INSERT INTO class (id,type, start_schedule, subject, courseedition_edition_id, classroom_classroom_id) VALUES
-- Course Edition 1
(1, 'TEORICA', '2025-02-17 10:00:00', 'Intro to CS - Theory', 1, 1),
(2, 'PL',      '2025-02-18 14:00:00', 'Intro to CS - Lab',    1, 2),

-- Course Edition 2
(3, 'TEORICA', '2025-02-19 09:00:00', 'Advanced Math - Theory', 2, 3),
(4, 'PL',      '2025-02-20 11:00:00', 'Advanced Math - Lab',    2, 4),

-- Course Edition 3
(5, 'TEORICA', '2025-02-21 15:00:00', 'Physics I - Theory', 3, 1),
(6, 'PL',      '2025-02-22 16:00:00', 'Physics I - Lab',    3, 2);


