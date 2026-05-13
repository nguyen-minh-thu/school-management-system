USE school_management;

-- 1. DROP USERS AND ROLES

DROP USER IF EXISTS 'teacher_user'@'localhost';
DROP USER IF EXISTS 'coordinator_user'@'localhost';
DROP USER IF EXISTS 'admin_user'@'localhost';

DROP ROLE IF EXISTS 'teacher_role';
DROP ROLE IF EXISTS 'coordinator_role';
DROP ROLE IF EXISTS 'admin_role';

-- 2. CREATE ROLES

CREATE ROLE 'teacher_role';
CREATE ROLE 'coordinator_role';
CREATE ROLE 'admin_role';

-- 3. CREATE USERS

CREATE USER 'teacher_user'@'localhost' IDENTIFIED BY 'teacher123';
CREATE USER 'coordinator_user'@'localhost' IDENTIFIED BY 'coordinator123';
CREATE USER 'admin_user'@'localhost' IDENTIFIED BY 'admin123';

-- 4. GRANT PRIVILEGES TO ROLES
-- Teacher Role
-- Teachers can view academic data and enter/update grades.
-- They should not delete important records.

GRANT SELECT ON school_management.Students TO 'teacher_role';
GRANT SELECT ON school_management.Classes TO 'teacher_role';
GRANT SELECT ON school_management.Subjects TO 'teacher_role';
GRANT SELECT ON school_management.Teachers TO 'teacher_role';
GRANT SELECT ON school_management.ClassSubjects TO 'teacher_role';
GRANT SELECT ON school_management.ClassSchedules TO 'teacher_role';

GRANT SELECT, INSERT, UPDATE ON school_management.Grades TO 'teacher_role';

-- Allow teachers to view useful reports
GRANT SELECT ON school_management.vw_class_roster TO 'teacher_role';
GRANT SELECT ON school_management.vw_class_subjects TO 'teacher_role';
GRANT SELECT ON school_management.vw_class_schedule TO 'teacher_role';
GRANT SELECT ON school_management.vw_subject_performance TO 'teacher_role';
GRANT SELECT ON school_management.vw_top_students TO 'teacher_role';

-- Allow teachers to use stored procedure and function
GRANT EXECUTE ON PROCEDURE school_management.sp_update_student_grade TO 'teacher_role';
GRANT EXECUTE ON FUNCTION school_management.fn_student_gpa TO 'teacher_role';

-- Coordinator Role
-- Academic coordinators can view all academic data and generate reports.
-- They can manage schedules and class-subject assignments.

GRANT SELECT ON school_management.* TO 'coordinator_role';

GRANT INSERT, UPDATE ON school_management.ClassSubjects TO 'coordinator_role';
GRANT INSERT, UPDATE ON school_management.ClassSchedules TO 'coordinator_role';
GRANT INSERT, UPDATE ON school_management.Classes TO 'coordinator_role';
GRANT INSERT, UPDATE ON school_management.Subjects TO 'coordinator_role';
GRANT INSERT, UPDATE ON school_management.Teachers TO 'coordinator_role';

GRANT EXECUTE ON PROCEDURE school_management.sp_update_student_grade TO 'coordinator_role';
GRANT EXECUTE ON FUNCTION school_management.fn_student_gpa TO 'coordinator_role';


-- Admin Role
-- Administrators have full control over the database.

GRANT ALL PRIVILEGES ON school_management.* TO 'admin_role';


-- 5. ASSIGN ROLES TO USERS

GRANT 'teacher_role' TO 'teacher_user'@'localhost';
GRANT 'coordinator_role' TO 'coordinator_user'@'localhost';
GRANT 'admin_role' TO 'admin_user'@'localhost';

SET DEFAULT ROLE 'teacher_role' TO 'teacher_user'@'localhost';
SET DEFAULT ROLE 'coordinator_role' TO 'coordinator_user'@'localhost';
SET DEFAULT ROLE 'admin_role' TO 'admin_user'@'localhost';

-- 6. BACKUP STRATEGY NOTES
-- Recommended manual backup command:
-- mysqldump -u root -p school_management > school_management_backup.sql
-- Recommended restore command:
-- mysql -u root -p school_management < school_management_backup.sql