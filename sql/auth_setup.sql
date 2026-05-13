USE school_management;

-- AUTHENTICATION SETUP FOR SCHOOL MANAGEMENT SYSTEM
-- This table is used by the Python/Tkinter application
-- to implement role-based login.

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(100) NOT NULL,
    Role ENUM('admin', 'teacher', 'student', 'coordinator') NOT NULL,
    StudentID INT NULL,
    TeacherID INT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_users_student
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT fk_users_teacher
        FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ADMIN AND COORDINATOR ACCOUNTS

INSERT INTO Users (Username, Password, Role, StudentID, TeacherID) VALUES
('admin', 'admin123', 'admin', NULL, NULL),
('coordinator', 'coordinator123', 'coordinator', NULL, NULL);

-- TEACHER ACCOUNTS
-- Automatically create one account for each teacher.
-- Username format: teacher01, teacher02, ...
-- Default password: teacher123

INSERT INTO Users (Username, Password, Role, StudentID, TeacherID)
SELECT
    CONCAT('teacher', LPAD(TeacherID, 2, '0')) AS Username,
    'teacher123' AS Password,
    'teacher' AS Role,
    NULL AS StudentID,
    TeacherID
FROM Teachers
ORDER BY TeacherID;

-- STUDENT ACCOUNTS
-- Automatically create one account for each student.
-- Username format: student01, student02, ...
-- Default password: student123

INSERT INTO Users (Username, Password, Role, StudentID, TeacherID)
SELECT
    CONCAT('student', LPAD(StudentID, 2, '0')) AS Username,
    'student123' AS Password,
    'student' AS Role,
    StudentID,
    NULL AS TeacherID
FROM Students
ORDER BY StudentID;

-- CHECK RESULT

SELECT 
    UserID,
    Username,
    Role,
    StudentID,
    TeacherID,
    CreatedAt
FROM Users
ORDER BY 
    FIELD(Role, 'admin', 'coordinator', 'teacher', 'student'),
    UserID;