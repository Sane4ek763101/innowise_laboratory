-- Deleting existing tables
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS students;

-- Creating tables
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    birth_year INTEGER
);

CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    grade INTEGER CHECK (grade >= 1 AND grade <= 100),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Inserting data
INSERT INTO students (full_name, birth_year) VALUES
('Alice Johnson', 2005),
('Brian Smith', 2004),
('Carla Reyes', 2006),
('Daniel Kim', 2005),
('Eva Thompson', 2003),
('Felix Nguyen', 2007),
('Grace Patel', 2005),
('Henry Lopez', 2004),
('Isabella Martinez', 2006);

INSERT INTO grades (student_id, subject, grade) VALUES
(1, 'Math', 88),
(1, 'English', 92),
(1, 'Science', 85),
(2, 'Math', 75),
(2, 'History', 83),
(2, 'English', 79),
(3, 'Science', 95),
(3, 'Math', 91),
(3, 'Art', 89),
(4, 'Math', 84),
(4, 'Science', 88),
(4, 'Physical Education', 93),
(5, 'English', 90),
(5, 'History', 85),
(5, 'Math', 88),
(6, 'Science', 72),
(6, 'Math', 78),
(6, 'English', 81),
(7, 'Art', 94),
(7, 'Science', 87),
(7, 'Math', 90),
(8, 'History', 77),
(8, 'Math', 83),
(8, 'Science', 80),
(9, 'English', 96),
(9, 'Math', 89),
(9, 'Art', 92);


-- Query 1: All of Alice Johnson's grades
SELECT '1. All Alice Johnson scores:' as '';
SELECT s.full_name, g.subject, g.grade
FROM grades g
JOIN students s ON g.student_id = s.id
WHERE s.full_name = 'Alice Johnson';
SELECT '' as '';

-- Query 2: Average grade for each student
SELECT '2. Average grade for each student:' as '';
SELECT s.full_name, ROUND(AVG(g.grade), 2) as average_grade
FROM students s
JOIN grades g ON s.id = g.student_id
GROUP BY s.id, s.full_name
ORDER BY average_grade DESC;
SELECT '' as '';

-- Query 3: Students born after 2004
SELECT '3. Students born after 2004:' as '';
SELECT full_name, birth_year
FROM students
WHERE birth_year > 2004;
SELECT '' as '';

-- Query 4: Average grades by subject
SELECT '4. Average grades by subject:' as '';
SELECT subject, ROUND(AVG(grade), 2) as average_grade
FROM grades
GROUP BY subject
ORDER BY average_grade DESC;
SELECT '' as '';

-- Query 5: Top 3 students with the highest average grades
SELECT '5. Top 3 students with the highest average grades:' as '';
SELECT s.full_name, ROUND(AVG(g.grade), 2) as average_grade
FROM students s
JOIN grades g ON s.id = g.student_id
GROUP BY s.id, s.full_name
ORDER BY average_grade DESC
LIMIT 3;
SELECT '' as '';

-- Query 6: Students with grades below 80
SELECT '6. Students with grades below 80:' as '';
SELECT DISTINCT s.full_name
FROM students s
JOIN grades g ON s.id = g.student_id
WHERE g.grade < 80
ORDER BY s.full_name;

-- Delete existing indexes
DROP INDEX IF EXISTS idx_grades_student_id;
DROP INDEX IF EXISTS idx_grades_subject;
DROP INDEX IF EXISTS idx_grades_grade;
DROP INDEX IF EXISTS idx_students_birth_year;

-- Creating new indexes
CREATE INDEX idx_grades_student_id ON grades(student_id);
CREATE INDEX idx_grades_subject ON grades(subject);
CREATE INDEX idx_grades_grade ON grades(grade);
CREATE INDEX idx_students_birth_year ON students(birth_year);
