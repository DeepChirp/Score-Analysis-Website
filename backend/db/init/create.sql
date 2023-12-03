CREATE TABLE scores (
    id  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    student_id INT UNSIGNED NOT NULL,
    exam_id INT UNSIGNED NOT NULL,
    subject_id INT UNSIGNED NOT NULL,
    semester_id INT UNSIGNED NOT NULL,
    value DOUBLE
);

CREATE TABLE students (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    class INT UNSIGNED NOT NULL,
    class_divide TINYINT UNSIGNED NOT NULL,
    grade_id INT UNSIGNED NOT NULL,
    name VARCHAR(16) NOT NULL
);

CREATE TABLE exams (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE subjects (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_score DOUBLE NOT NULL,
    name VARCHAR(16) NOT NULL
);

CREATE TABLE semesters (
    id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    class_divide TINYINT UNSIGNED NOT NULL
);

CREATE TABLE grades (
    id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL
);

CREATE TABLE uploads (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    unique_id BIGINT UNSIGNED,
    filename VARCHAR(255)
);

CREATE INDEX idx_student_id ON scores (student_id);
CREATE INDEX idx_exam_id ON scores (exam_id);
CREATE INDEX idx_class ON students (class);
CREATE INDEX idx_student_id_exam_id ON scores (student_id, exam_id);