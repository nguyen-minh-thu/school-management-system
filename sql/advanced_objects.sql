USE school_management;

-- DROP OLD OBJECTS

DROP VIEW IF EXISTS vw_class_roster;
DROP VIEW IF EXISTS vw_top_students;
DROP VIEW IF EXISTS vw_subject_performance;
DROP VIEW IF EXISTS vw_teacher_load_summary;
DROP VIEW IF EXISTS vw_class_schedule;
DROP VIEW IF EXISTS vw_teacher_assignment_report;
DROP VIEW IF EXISTS vw_class_subjects;

DROP PROCEDURE IF EXISTS sp_update_student_grade;

DROP FUNCTION IF EXISTS fn_student_gpa;

DROP TRIGGER IF EXISTS trg_check_grade_before_insert;
DROP TRIGGER IF EXISTS trg_check_grade_before_update;
DROP TRIGGER IF EXISTS trg_check_schedule_before_insert;
DROP TRIGGER IF EXISTS trg_check_schedule_before_update;
DROP TRIGGER IF EXISTS trg_update_class_performance_after_grade_insert;
DROP TRIGGER IF EXISTS trg_update_class_performance_after_grade_update;
DROP TRIGGER IF EXISTS trg_update_class_performance_after_grade_delete;

-- 1. INDEXES

CREATE INDEX idx_students_name ON Students(StudentName);
CREATE INDEX idx_students_class ON Students(ClassID);

CREATE INDEX idx_teachers_name ON Teachers(TeacherName);
CREATE INDEX idx_teachers_subject ON Teachers(Subject);

CREATE INDEX idx_grades_student ON Grades(StudentID);
CREATE INDEX idx_grades_subject ON Grades(SubjectID);
CREATE INDEX idx_grades_score ON Grades(Score);

CREATE INDEX idx_class_subjects_class ON ClassSubjects(ClassID);
CREATE INDEX idx_class_subjects_subject ON ClassSubjects(SubjectID);

CREATE INDEX idx_schedule_class ON ClassSchedules(ClassID);
CREATE INDEX idx_schedule_subject ON ClassSchedules(SubjectID);
CREATE INDEX idx_schedule_teacher ON ClassSchedules(TeacherID);

-- 2. VIEWS

-- View 1: Class roster
CREATE OR REPLACE VIEW vw_class_roster AS
SELECT 
    c.ClassID,
    c.ClassName,
    s.StudentID,
    s.StudentName,
    s.BirthDate,
    s.Address
FROM Classes c
LEFT JOIN Students s 
    ON c.ClassID = s.ClassID
ORDER BY c.ClassName, s.StudentName;


-- View 2: Class subjects
CREATE OR REPLACE VIEW vw_class_subjects AS
SELECT
    c.ClassID,
    c.ClassName,
    sub.SubjectID,
    sub.SubjectName
FROM Classes c
LEFT JOIN ClassSubjects csb
    ON c.ClassID = csb.ClassID
LEFT JOIN Subjects sub
    ON csb.SubjectID = sub.SubjectID
ORDER BY c.ClassName, sub.SubjectName;


-- View 3: Top students
CREATE OR REPLACE VIEW vw_top_students AS
SELECT 
    s.StudentID,
    s.StudentName,
    c.ClassName,
    ROUND(AVG(g.Score), 2) AS AverageScore
FROM Students s
JOIN Classes c 
    ON s.ClassID = c.ClassID
LEFT JOIN Grades g 
    ON s.StudentID = g.StudentID
GROUP BY s.StudentID, s.StudentName, c.ClassName
ORDER BY AverageScore DESC;


-- View 4: Subject-wise performance
CREATE OR REPLACE VIEW vw_subject_performance AS
SELECT 
    sub.SubjectID,
    sub.SubjectName,
    COUNT(g.GradeID) AS NumberOfGrades,
    ROUND(AVG(g.Score), 2) AS AverageScore,
    MIN(g.Score) AS MinScore,
    MAX(g.Score) AS MaxScore
FROM Subjects sub
LEFT JOIN Grades g 
    ON sub.SubjectID = g.SubjectID
GROUP BY sub.SubjectID, sub.SubjectName
ORDER BY sub.SubjectName;


-- View 5: Teacher load summary
CREATE OR REPLACE VIEW vw_teacher_load_summary AS
SELECT
    t.TeacherID,
    t.TeacherName,
    t.Subject,
    COUNT(DISTINCT cs.ClassID) AS NumberOfClasses,
    COUNT(cs.ScheduleID) AS NumberOfSessions
FROM Teachers t
LEFT JOIN ClassSchedules cs 
    ON t.TeacherID = cs.TeacherID
GROUP BY 
    t.TeacherID,
    t.TeacherName,
    t.Subject
ORDER BY t.TeacherName;


-- View 6: Class schedule
CREATE OR REPLACE VIEW vw_class_schedule AS
SELECT
    c.ClassID,
    c.ClassName,
    sub.SubjectID,
    sub.SubjectName,
    cs.ScheduleID,
    t.TeacherID,
    t.TeacherName,
    cs.DayOfWeek,
    cs.StartTime,
    cs.EndTime,
    cs.Room
FROM Classes c
LEFT JOIN ClassSubjects csb
    ON c.ClassID = csb.ClassID
LEFT JOIN Subjects sub
    ON csb.SubjectID = sub.SubjectID
LEFT JOIN ClassSchedules cs
    ON c.ClassID = cs.ClassID
    AND sub.SubjectID = cs.SubjectID
LEFT JOIN Teachers t
    ON cs.TeacherID = t.TeacherID
ORDER BY 
    c.ClassName,
    FIELD(cs.DayOfWeek, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    cs.StartTime,
    sub.SubjectName;


-- View 7: Teacher assignment report
CREATE OR REPLACE VIEW vw_teacher_assignment_report AS
SELECT
    t.TeacherID,
    t.TeacherName,
    t.Subject AS Specialization,
    c.ClassName,
    sub.SubjectName,
    cs.DayOfWeek,
    cs.StartTime,
    cs.EndTime,
    cs.Room
FROM Teachers t
LEFT JOIN ClassSchedules cs 
    ON t.TeacherID = cs.TeacherID
LEFT JOIN Classes c 
    ON cs.ClassID = c.ClassID
LEFT JOIN Subjects sub 
    ON cs.SubjectID = sub.SubjectID
ORDER BY 
    t.TeacherName,
    c.ClassName,
    FIELD(cs.DayOfWeek, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    cs.StartTime;

-- 3. STORED PROCEDURE

DELIMITER //

CREATE PROCEDURE sp_update_student_grade(
    IN p_GradeID INT,
    IN p_NewScore DECIMAL(4,1)
)
BEGIN
    IF p_NewScore < 0 OR p_NewScore > 10 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid score: score must be between 0 and 10';
    END IF;

    UPDATE Grades
    SET Score = p_NewScore
    WHERE GradeID = p_GradeID;
END //

DELIMITER ;

-- 4. FUNCTION

DELIMITER //

CREATE FUNCTION fn_student_gpa(p_StudentID INT)
RETURNS DECIMAL(4,2)
DETERMINISTIC
BEGIN
    DECLARE v_gpa DECIMAL(4,2);

    SELECT ROUND(AVG(Score), 2)
    INTO v_gpa
    FROM Grades
    WHERE StudentID = p_StudentID;

    RETURN v_gpa;
END //

DELIMITER ;

-- 5. TRIGGER SUPPORT TABLE

CREATE TABLE IF NOT EXISTS ClassPerformanceStats (
    ClassID INT PRIMARY KEY,
    AverageScore DECIMAL(4,2),
    LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
);

-- Insert / refresh initial class performance stats
INSERT INTO ClassPerformanceStats (ClassID, AverageScore)
SELECT 
    c.ClassID,
    ROUND(AVG(g.Score), 2) AS AverageScore
FROM Classes c
LEFT JOIN Students s 
    ON c.ClassID = s.ClassID
LEFT JOIN Grades g 
    ON s.StudentID = g.StudentID
GROUP BY c.ClassID
ON DUPLICATE KEY UPDATE 
    AverageScore = VALUES(AverageScore);

-- 6. VALIDATION TRIGGERS

-- Check before inserting grade:
-- 1. Score must be 0-10
-- 2. Subject must belong to student's class
DELIMITER //

CREATE TRIGGER trg_check_grade_before_insert
BEFORE INSERT ON Grades
FOR EACH ROW
BEGIN
    DECLARE v_class_id INT;
    DECLARE v_count INT;

    IF NEW.Score < 0 OR NEW.Score > 10 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid grade: score must be between 0 and 10';
    END IF;

    SELECT ClassID
    INTO v_class_id
    FROM Students
    WHERE StudentID = NEW.StudentID;

    SELECT COUNT(*)
    INTO v_count
    FROM ClassSubjects
    WHERE ClassID = v_class_id
      AND SubjectID = NEW.SubjectID;

    IF v_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid grade: this subject is not assigned to the student class';
    END IF;
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER trg_check_grade_before_update
BEFORE UPDATE ON Grades
FOR EACH ROW
BEGIN
    DECLARE v_class_id INT;
    DECLARE v_count INT;

    IF NEW.Score < 0 OR NEW.Score > 10 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid grade: score must be between 0 and 10';
    END IF;

    SELECT ClassID
    INTO v_class_id
    FROM Students
    WHERE StudentID = NEW.StudentID;

    SELECT COUNT(*)
    INTO v_count
    FROM ClassSubjects
    WHERE ClassID = v_class_id
      AND SubjectID = NEW.SubjectID;

    IF v_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid grade: this subject is not assigned to the student class';
    END IF;
END //

DELIMITER ;


-- Check before inserting schedule:
-- 1. Subject must belong to class
-- 2. Teacher specialization must match subject name
DELIMITER //

CREATE TRIGGER trg_check_schedule_before_insert
BEFORE INSERT ON ClassSchedules
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    DECLARE v_subject_name VARCHAR(100);
    DECLARE v_teacher_subject VARCHAR(100);

    SELECT COUNT(*)
    INTO v_count
    FROM ClassSubjects
    WHERE ClassID = NEW.ClassID
      AND SubjectID = NEW.SubjectID;

    IF v_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid schedule: this subject is not assigned to this class';
    END IF;

    SELECT SubjectName
    INTO v_subject_name
    FROM Subjects
    WHERE SubjectID = NEW.SubjectID;

    SELECT Subject
    INTO v_teacher_subject
    FROM Teachers
    WHERE TeacherID = NEW.TeacherID;

    IF v_subject_name <> v_teacher_subject THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid schedule: teacher specialization does not match subject';
    END IF;
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER trg_check_schedule_before_update
BEFORE UPDATE ON ClassSchedules
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    DECLARE v_subject_name VARCHAR(100);
    DECLARE v_teacher_subject VARCHAR(100);

    SELECT COUNT(*)
    INTO v_count
    FROM ClassSubjects
    WHERE ClassID = NEW.ClassID
      AND SubjectID = NEW.SubjectID;

    IF v_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid schedule: this subject is not assigned to this class';
    END IF;

    SELECT SubjectName
    INTO v_subject_name
    FROM Subjects
    WHERE SubjectID = NEW.SubjectID;

    SELECT Subject
    INTO v_teacher_subject
    FROM Teachers
    WHERE TeacherID = NEW.TeacherID;

    IF v_subject_name <> v_teacher_subject THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid schedule: teacher specialization does not match subject';
    END IF;
END //

DELIMITER ;

-- 7. PERFORMANCE UPDATE TRIGGERS

-- After inserting grade
DELIMITER //

CREATE TRIGGER trg_update_class_performance_after_grade_insert
AFTER INSERT ON Grades
FOR EACH ROW
BEGIN
    INSERT INTO ClassPerformanceStats (ClassID, AverageScore)
    SELECT 
        s.ClassID,
        ROUND(AVG(g.Score), 2)
    FROM Students s
    JOIN Grades g 
        ON s.StudentID = g.StudentID
    WHERE s.ClassID = (
        SELECT ClassID 
        FROM Students 
        WHERE StudentID = NEW.StudentID
    )
    GROUP BY s.ClassID
    ON DUPLICATE KEY UPDATE 
        AverageScore = VALUES(AverageScore);
END //

DELIMITER ;


-- After updating grade
DELIMITER //

CREATE TRIGGER trg_update_class_performance_after_grade_update
AFTER UPDATE ON Grades
FOR EACH ROW
BEGIN
    INSERT INTO ClassPerformanceStats (ClassID, AverageScore)
    SELECT 
        s.ClassID,
        ROUND(AVG(g.Score), 2)
    FROM Students s
    JOIN Grades g 
        ON s.StudentID = g.StudentID
    WHERE s.ClassID = (
        SELECT ClassID 
        FROM Students 
        WHERE StudentID = NEW.StudentID
    )
    GROUP BY s.ClassID
    ON DUPLICATE KEY UPDATE 
        AverageScore = VALUES(AverageScore);
END //

DELIMITER ;


-- After deleting grade
DELIMITER //

CREATE TRIGGER trg_update_class_performance_after_grade_delete
AFTER DELETE ON Grades
FOR EACH ROW
BEGIN
    INSERT INTO ClassPerformanceStats (ClassID, AverageScore)
    SELECT 
        s.ClassID,
        ROUND(AVG(g.Score), 2)
    FROM Students s
    LEFT JOIN Grades g 
        ON s.StudentID = g.StudentID
    WHERE s.ClassID = (
        SELECT ClassID 
        FROM Students 
        WHERE StudentID = OLD.StudentID
    )
    GROUP BY s.ClassID
    ON DUPLICATE KEY UPDATE 
        AverageScore = VALUES(AverageScore);
END //

DELIMITER ;