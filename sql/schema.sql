DROP DATABASE IF EXISTS school_management;
CREATE DATABASE school_management;
USE school_management;

-- 1. SUBJECTS

CREATE TABLE Subjects (
    SubjectID INT PRIMARY KEY,
    SubjectName VARCHAR(100) NOT NULL UNIQUE
);

-- 2. TEACHERS
-- Subject is used as teacher specialization.
-- It should match Subjects.SubjectName in sample data.

CREATE TABLE Teachers (
    TeacherID INT PRIMARY KEY,
    TeacherName VARCHAR(100) NOT NULL,
    Subject VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE
);

-- 3. CLASSES
-- TeacherID here is used as the homeroom/advisory teacher.

CREATE TABLE Classes (
    ClassID INT PRIMARY KEY,
    ClassName VARCHAR(50) NOT NULL UNIQUE,
    TeacherID INT NOT NULL,

    CONSTRAINT fk_classes_teacher
        FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- 4. STUDENTS

CREATE TABLE Students (
    StudentID INT PRIMARY KEY,
    StudentName VARCHAR(100) NOT NULL,
    BirthDate DATE,
    ClassID INT NOT NULL,
    Address VARCHAR(255),

    CONSTRAINT fk_students_class
        FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- 5. CLASS SUBJECTS
-- This table defines which subjects each class studies.

CREATE TABLE ClassSubjects (
    ClassID INT NOT NULL,
    SubjectID INT NOT NULL,

    PRIMARY KEY (ClassID, SubjectID),

    CONSTRAINT fk_classsubjects_class
        FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_classsubjects_subject
        FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- 6. GRADES
-- Grades are assigned to students by subject.
-- Additional logic checking whether the subject belongs to the student's class
-- is handled by triggers in advanced_objects.sql.

CREATE TABLE Grades (
    GradeID INT PRIMARY KEY,
    StudentID INT NOT NULL,
    SubjectID INT NOT NULL,
    Score DECIMAL(4,1) NOT NULL,

    CONSTRAINT fk_grades_student
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_grades_subject
        FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_grades_score
        CHECK (Score >= 0 AND Score <= 10),

    CONSTRAINT uq_student_subject
        UNIQUE (StudentID, SubjectID)
);

-- 7. CLASS SCHEDULES
-- Each schedule row represents one subject session of one class.

CREATE TABLE ClassSchedules (
    ScheduleID INT PRIMARY KEY,
    ClassID INT NOT NULL,
    SubjectID INT NOT NULL,
    TeacherID INT NOT NULL,
    DayOfWeek ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    Room VARCHAR(50),

    CONSTRAINT fk_schedule_class
        FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_schedule_subject
        FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_schedule_teacher
        FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_schedule_time
        CHECK (StartTime < EndTime),

    CONSTRAINT uq_class_time
        UNIQUE (ClassID, DayOfWeek, StartTime),

    CONSTRAINT uq_room_time
        UNIQUE (Room, DayOfWeek, StartTime)
);