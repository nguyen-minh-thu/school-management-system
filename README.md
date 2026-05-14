# School Management System

## Demo Video

YouTube demo link:

```text
https://youtu.be/_tMwnfpAbFM
```

## Link app
```
https://drive.google.com/file/d/1aaSvM5OaX8XK9lDrcVRNxHcmiOwRxOEV/view?usp=sharing
```

## 1. Project Overview

The School Management System is a database management project developed using MySQL and Python Tkinter.  
The system supports managing students, teachers, classes, subjects, grades, class schedules, and academic reports.

The application also includes role-based login for different users such as admin, teacher, student, and academic coordinator.

---

## 2. Main Features

- Manage student records
- Manage teachers and subject specialization
- Create classes and subjects
- Assign subjects to classes
- Create class schedules
- Enter and update student grades
- View academic reports
- View class roster and class schedule
- View teacher workload and assignment reports
- Role-based login system

---

## 3. Project Structure

```text
school-management-system/
│
├── sql/
│   ├── schema.sql
│   ├── school_sample_data.sql
│   ├── advanced_objects.sql
│   ├── auth_setup.sql
│   └── security_backup.sql
│
├── python/
│   ├── desktop_app.py
│   ├── db_config.py
│   ├── desktop_app.spec
│   └── generate_sample_data.py
│
├── docs/
│   ├── report.pdf
│   ├── ER_diagram.mwb.bak
│   ├── ER_diagram.mwb
│   ├── 17.pdf (project requirement)
│   └── ER_diagram.png
│
└── README.md
````

---

## 4. How to Run the Project

### Step 1: Install Python Libraries

```bash
pip install mysql-connector-python faker
```

---

### Step 2: Configure Database Connection

Open:

```text
python/db_config.py
```

Update your MySQL password:

```python
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="PASSWORD",
    database="school_management"
)
```

---

### Step 3: Run SQL Files in MySQL Workbench

Run the SQL files in this exact order:

```text
1. schema.sql
2. school_sample_data.sql
3. advanced_objects.sql
4. auth_setup.sql
5. security_backup.sql
```

---

### Step 4: Run the Python Application

```bash
cd python
python desktop_app.py
```

---

## 5. Default Login Accounts

### Admin

```text
Username: admin
Password: admin123
```

### Coordinator

```text
Username: coordinator
Password: coordinator123
```

### Teacher

```text
Username: teacher01
Password: teacher123
```

### Student

```text
Username: student01
Password: student123
```

## 6. Notes

* MySQL Server must be installed and running before opening the application.
* Users do not need to run Python scripts manually. However, because the project uses MySQL as required, MySQL Server must be installed on the target machine. The database must also be created and initialized before the application can connect successfully.
* The application uses Tkinter for the desktop interface.
* Sample data is generated using Python Faker.
* Passwords are stored as plain text for demo purposes only.
* In a real system, passwords should be securely hashed.
