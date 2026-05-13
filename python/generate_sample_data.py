from faker import Faker
import random
import os

fake = Faker("en_US")
random.seed(42)
Faker.seed(42)

OUTPUT_FILE = "school_sample_data.sql"

print("Current working directory:", os.getcwd())
print("Output file will be saved at:", os.path.abspath(OUTPUT_FILE))

# CONFIG
NUM_SUBJECTS = 10
NUM_TEACHERS = 15
NUM_CLASSES = 8
NUM_STUDENTS = 80

SUBJECTS_PER_CLASS = 5

# If True: every student has grades for all subjects of their class
GENERATE_FULL_GRADES = True

# FIXED SUBJECTS
subject_names = [
    "Database Systems",
    "Python Programming",
    "Mathematics",
    "English",
    "Data Structures",
    "Statistics",
    "Computer Networks",
    "Software Engineering",
    "Operating Systems",
    "Business Management"
]

subjects = []
for i, name in enumerate(subject_names[:NUM_SUBJECTS], start=1):
    subjects.append({
        "SubjectID": i,
        "SubjectName": name
    })

subject_by_id = {s["SubjectID"]: s for s in subjects}

# TEACHERS
# Make sure every subject has at least one teacher
teachers = []

teacher_id = 1

# First 10 teachers: one teacher for each subject
for subject in subjects:
    teachers.append({
        "TeacherID": teacher_id,
        "TeacherName": fake.name(),
        "SubjectID": subject["SubjectID"],
        "Subject": subject["SubjectName"],
        "Email": f"teacher{teacher_id:03d}@school.edu"
    })
    teacher_id += 1

# Extra teachers: randomly assigned to subjects
while teacher_id <= NUM_TEACHERS:
    subject = random.choice(subjects)
    teachers.append({
        "TeacherID": teacher_id,
        "TeacherName": fake.name(),
        "SubjectID": subject["SubjectID"],
        "Subject": subject["SubjectName"],
        "Email": f"teacher{teacher_id:03d}@school.edu"
    })
    teacher_id += 1

teachers_by_subject = {}
for t in teachers:
    teachers_by_subject.setdefault(t["SubjectID"], []).append(t)

# CLASSES
# TeacherID here can be understood as homeroom teacher
class_names = [
    "SE1701", "SE1702", "SE1703",
    "DB1701", "DB1702",
    "AI1701", "IS1701", "BA1701"
]

classes = []
for i in range(1, NUM_CLASSES + 1):
    classes.append({
        "ClassID": i,
        "ClassName": class_names[i - 1],
        "TeacherID": random.choice(teachers)["TeacherID"]
    })

# CLASS_SUBJECTS
# Each class studies exactly SUBJECTS_PER_CLASS subjects
class_subjects = []

# Manual design to make data look realistic and stable
class_subject_map = {
    1: [1, 2, 5, 8, 10],      # SE1701
    2: [1, 2, 5, 7, 10],      # SE1702
    3: [2, 5, 7, 8, 9],       # SE1703
    4: [1, 2, 3, 6, 10],      # DB1701
    5: [1, 3, 6, 8, 10],      # DB1702
    6: [2, 3, 5, 8, 9],       # AI1701
    7: [1, 2, 5, 8, 10],      # IS1701
    8: [3, 4, 6, 10, 1]       # BA1701
}

for class_item in classes:
    class_id = class_item["ClassID"]
    for subject_id in class_subject_map[class_id]:
        class_subjects.append({
            "ClassID": class_id,
            "SubjectID": subject_id
        })

subjects_by_class = {}
for cs in class_subjects:
    subjects_by_class.setdefault(cs["ClassID"], []).append(cs["SubjectID"])

# STUDENTS
# Each student belongs to exactly one class
students = []

for i in range(1, NUM_STUDENTS + 1):
    class_item = random.choice(classes)

    students.append({
        "StudentID": i,
        "StudentName": fake.name(),
        "BirthDate": fake.date_of_birth(minimum_age=16, maximum_age=22).strftime("%Y-%m-%d"),
        "ClassID": class_item["ClassID"],
        "Address": fake.address().replace("\n", ", ")
    })

# GRADES
# A student's grades must match subjects of the student's class
grades = []
grade_id = 1

if GENERATE_FULL_GRADES:
    for student in students:
        class_id = student["ClassID"]
        allowed_subject_ids = subjects_by_class[class_id]

        for subject_id in allowed_subject_ids:
            grades.append({
                "GradeID": grade_id,
                "StudentID": student["StudentID"],
                "SubjectID": subject_id,
                "Score": round(random.uniform(4.0, 10.0), 1)
            })
            grade_id += 1
else:
    # Optional: if you want fewer grades, generate 3 random valid subjects per student
    for student in students:
        class_id = student["ClassID"]
        allowed_subject_ids = subjects_by_class[class_id]
        selected_subject_ids = random.sample(allowed_subject_ids, k=3)

        for subject_id in selected_subject_ids:
            grades.append({
                "GradeID": grade_id,
                "StudentID": student["StudentID"],
                "SubjectID": subject_id,
                "Score": round(random.uniform(4.0, 10.0), 1)
            })
            grade_id += 1

# CLASS SCHEDULES
# Schedule must match class_subjects and teacher's subject
schedules = []

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
rooms = ["A101", "A102", "B201", "B202", "C301", "C302", "D401", "D402"]
time_slots = [
    ("08:00:00", "09:30:00"),
    ("09:45:00", "11:15:00"),
    ("13:30:00", "15:00:00"),
    ("15:15:00", "16:45:00")
]

used_class_time_slots = set()
used_room_time_slots = set()

schedule_id = 1

# Create one schedule row for every class-subject pair
for cs in class_subjects:
    class_id = cs["ClassID"]
    subject_id = cs["SubjectID"]

    teacher = random.choice(teachers_by_subject[subject_id])

    placed = False
    attempts = 0

    while not placed and attempts < 200:
        day = random.choice(days)
        start_time, end_time = random.choice(time_slots)
        room = random.choice(rooms)

        class_time_slot = (class_id, day, start_time)
        room_time_slot = (room, day, start_time)

        if class_time_slot not in used_class_time_slots and room_time_slot not in used_room_time_slots:
            used_class_time_slots.add(class_time_slot)
            used_room_time_slots.add(room_time_slot)

            schedules.append({
                "ScheduleID": schedule_id,
                "ClassID": class_id,
                "SubjectID": subject_id,
                "TeacherID": teacher["TeacherID"],
                "DayOfWeek": day,
                "StartTime": start_time,
                "EndTime": end_time,
                "Room": room
            })

            schedule_id += 1
            placed = True

        attempts += 1

    if not placed:
        raise Exception(f"Could not create schedule for ClassID={class_id}, SubjectID={subject_id}")

# HELPER
def sql_escape(value):
    return str(value).replace("'", "''")

# WRITE SQL FILE
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("-- SCHOOL MANAGEMENT SYSTEM SAMPLE DATA\n")
    f.write("-- Generated by Python Faker\n\n")

    f.write("USE school_management;\n\n")

    f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
    f.write("TRUNCATE TABLE ClassSchedules;\n")
    f.write("TRUNCATE TABLE Grades;\n")
    f.write("TRUNCATE TABLE ClassSubjects;\n")
    f.write("TRUNCATE TABLE Students;\n")
    f.write("TRUNCATE TABLE Classes;\n")
    f.write("TRUNCATE TABLE Teachers;\n")
    f.write("TRUNCATE TABLE Subjects;\n")
    f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")

    f.write("-- 1. Subjects\n")
    for s in subjects:
        f.write(
            f"INSERT INTO Subjects (SubjectID, SubjectName) VALUES "
            f"({s['SubjectID']}, '{sql_escape(s['SubjectName'])}');\n"
        )

    f.write("\n-- 2. Teachers\n")
    for t in teachers:
        # If Teachers table only has column Subject, use this version:
        f.write(
            f"INSERT INTO Teachers (TeacherID, TeacherName, Subject, Email) VALUES "
            f"({t['TeacherID']}, '{sql_escape(t['TeacherName'])}', "
            f"'{sql_escape(t['Subject'])}', '{sql_escape(t['Email'])}');\n"
        )

        # If Teachers table has SubjectID instead of Subject, use this instead:
        # f.write(
        #     f"INSERT INTO Teachers (TeacherID, TeacherName, SubjectID, Email) VALUES "
        #     f"({t['TeacherID']}, '{sql_escape(t['TeacherName'])}', "
        #     f"{t['SubjectID']}, '{sql_escape(t['Email'])}');\n"
        # )

    f.write("\n-- 3. Classes\n")
    for c in classes:
        f.write(
            f"INSERT INTO Classes (ClassID, ClassName, TeacherID) VALUES "
            f"({c['ClassID']}, '{sql_escape(c['ClassName'])}', {c['TeacherID']});\n"
        )

    f.write("\n-- 4. ClassSubjects\n")
    for cs in class_subjects:
        f.write(
            f"INSERT INTO ClassSubjects (ClassID, SubjectID) VALUES "
            f"({cs['ClassID']}, {cs['SubjectID']});\n"
        )

    f.write("\n-- 5. Students\n")
    for s in students:
        f.write(
            f"INSERT INTO Students (StudentID, StudentName, BirthDate, ClassID, Address) VALUES "
            f"({s['StudentID']}, '{sql_escape(s['StudentName'])}', "
            f"'{s['BirthDate']}', {s['ClassID']}, '{sql_escape(s['Address'])}');\n"
        )

    f.write("\n-- 6. Grades\n")
    for g in grades:
        f.write(
            f"INSERT INTO Grades (GradeID, StudentID, SubjectID, Score) VALUES "
            f"({g['GradeID']}, {g['StudentID']}, {g['SubjectID']}, {g['Score']});\n"
        )

    f.write("\n-- 7. Class Schedules\n")
    for sc in schedules:
        f.write(
            f"INSERT INTO ClassSchedules "
            f"(ScheduleID, ClassID, SubjectID, TeacherID, DayOfWeek, StartTime, EndTime, Room) VALUES "
            f"({sc['ScheduleID']}, {sc['ClassID']}, {sc['SubjectID']}, {sc['TeacherID']}, "
            f"'{sql_escape(sc['DayOfWeek'])}', '{sc['StartTime']}', '{sc['EndTime']}', "
            f"'{sql_escape(sc['Room'])}');\n"
        )

print(f"Done! SQL file generated at: {OUTPUT_FILE}")
print(f"Subjects: {len(subjects)} rows")
print(f"Teachers: {len(teachers)} rows")
print(f"Classes: {len(classes)} rows")
print(f"ClassSubjects: {len(class_subjects)} rows")
print(f"Students: {len(students)} rows")
print(f"Grades: {len(grades)} rows")
print(f"ClassSchedules: {len(schedules)} rows")
print(
    "Total rows:",
    len(subjects)
    + len(teachers)
    + len(classes)
    + len(class_subjects)
    + len(students)
    + len(grades)
    + len(schedules),
    "rows"
)