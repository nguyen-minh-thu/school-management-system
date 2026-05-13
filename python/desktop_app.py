import tkinter as tk
from tkinter import ttk, messagebox

from streamlit import form
from db_config import get_connection


class SchoolManagementApp:
    def _on_mousewheel(self, event):
     self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("900x600")

        self.current_user = None

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.container)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
         "<Configure>",
         lambda e: self.canvas.configure(
           scrollregion=self.canvas.bbox("all")
         )
        )

        self.canvas_window = self.canvas.create_window(
         (0, 0),
         window=self.scrollable_frame,
         anchor="n"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.main_frame = self.scrollable_frame

        def resize_scrollable_frame(event):
           self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", resize_scrollable_frame)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.show_login_screen()

    # =========================
    # COMMON UI HELPERS
    # =========================
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            self.canvas.yview_moveto(0)

    def create_title(self, text):
        title = tk.Label(
            self.main_frame,
            text=text,
            font=("Arial", 20, "bold")
        )
        title.pack(pady=20)

    def create_button(self, text, command):
        btn = tk.Button(
            self.main_frame,
            text=text,
            width=30,
            height=2,
            command=command
        )
        btn.pack(pady=6)

    def view_table_data(self, table_name):
     self.clear_frame()
     self.create_title(f"Table: {table_name}")

     try:
        conn = get_connection()

        if conn is None:
            messagebox.showerror("Connection Error", "Cannot connect to database.")
            return

        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        cursor.close()
        conn.close()

        table_frame = tk.Frame(self.main_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree_scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_x = tk.Scrollbar(table_frame, orient="horizontal")

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )

        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)

        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")

        for row in rows:
            tree.insert("", "end", values=row)

        tk.Button(
            self.main_frame,
            text="Back to All Tables",
            width=25,
            command=self.show_all_tables
        ).pack(pady=5)

        tk.Button(
            self.main_frame,
            text="Back to Dashboard",
            width=25,
            command=self.show_admin_dashboard
        ).pack(pady=5)

     except Exception as e:
        messagebox.showerror("Query Error", str(e))

    def show_table(self, title, columns, rows):
        self.clear_frame()
        self.create_title(title)

        table_frame = tk.Frame(self.main_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")

        for row in rows:
            tree.insert("", tk.END, values=row)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=y_scroll.set)

        tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        self.create_button("Back to Dashboard", self.show_dashboard)

    def fetch_all(self, sql, params=None):
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Database Error", "Cannot connect to database.")
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            messagebox.showerror("Query Error", str(e))
            return []
        finally:
            cursor.close()
            conn.close()

    def execute_query(self, sql, params=None):
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Database Error", "Cannot connect to database.")
            return False

        try:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Execution Error", str(e))
            return False
        finally:
            cursor.close()
            conn.close()

    # =========================
    # LOGIN
    # =========================
    def show_login_screen(self):
        self.clear_frame()

        self.create_title("School Management System")

        login_box = tk.Frame(self.main_frame)
        login_box.pack(pady=20)

        tk.Label(login_box, text="Username:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(login_box, text="Password:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)

        self.username_entry = tk.Entry(login_box, width=30)
        self.password_entry = tk.Entry(login_box, width=30, show="*")

        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(
            login_box,
            text="Login",
            width=20,
            command=self.login
        ).grid(row=2, column=0, columnspan=2, pady=15)

        tk.Label(
            self.main_frame,
            text="Demo accounts: admin/admin123 | teacher01/teacher123 | student01/student123 | coordinator/coordinator123",
            font=("Arial", 10)
        ).pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        sql = """
            SELECT UserID, Username, Role, StudentID, TeacherID
            FROM Users
            WHERE Username = %s AND Password = %s
        """

        rows = self.fetch_all(sql, (username, password))

        if not rows:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return

        user_id, username, role, student_id, teacher_id = rows[0]

        self.current_user = {
            "UserID": user_id,
            "Username": username,
            "Role": role,
            "StudentID": student_id,
            "TeacherID": teacher_id
        }

        messagebox.showinfo("Login Successful", f"Welcome, {username} ({role})")
        self.show_dashboard()

    # =========================
    # DASHBOARD ROUTER
    # =========================
    def show_dashboard(self):
        if self.current_user is None:
            self.show_login_screen()
            return

        role = self.current_user["Role"]

        if role == "admin":
            self.show_admin_dashboard()
        elif role == "teacher":
            self.show_teacher_dashboard()
        elif role == "student":
            self.show_student_dashboard()
        elif role == "coordinator":
            self.show_coordinator_dashboard()
        else:
            messagebox.showerror("Role Error", "Unknown role.")
            self.show_login_screen()

    def logout(self):
        self.current_user = None
        self.show_login_screen()

    # =========================
    # ADMIN DASHBOARD
    # =========================
    def show_admin_dashboard(self):
        self.clear_frame()
        self.create_title("Admin Dashboard")
        tk.Button(
         self.main_frame,
         text="View All Tables",
         width=30,
         command=self.show_all_tables
        ).pack(pady=5)

        self.create_button("Add New Student", self.show_add_student_form)
        self.create_button("Update Student Address", self.show_update_student_form)
        self.create_button("Add New Subject", self.show_add_subject_form)
        self.create_button("Create New Class", self.show_create_class_form)
        tk.Button(
            self.main_frame,
            text="Assign Subject to Class",
            width=30,
            command=self.show_assign_subject_to_class_form
        ).pack(pady=5)
        self.create_button("Create Class Schedule", self.show_create_schedule_form)
        self.create_button("Enter New Grade", self.show_enter_grade_form)
        self.create_button("View Class Roster", self.show_class_roster_form)
        self.create_button("View Class Schedule", self.view_class_schedule)
        self.create_button("View Top Students", self.view_top_students)
        self.create_button("View Subject Performance", self.view_subject_performance)
        self.create_button("View Teacher Load Summary", self.view_teacher_load_summary)
        self.create_button("View Teacher Assignment Report", self.view_teacher_assignment_report)
        self.create_button("Logout", self.logout)

    # =========================
    # TEACHER DASHBOARD
    # =========================
    def show_teacher_dashboard(self):
        self.clear_frame()
        self.create_title("Teacher Dashboard")

        self.create_button("View Class Roster", self.show_class_roster_form)
        self.create_button("View Class Schedule", self.view_class_schedule)
        self.create_button("Enter New Grade", self.show_enter_grade_form)
        self.create_button("View Subject Performance", self.view_subject_performance)
        self.create_button("View Teacher Load Summary", self.view_teacher_load_summary)
        self.create_button("View Teacher Assignment Report", self.view_teacher_assignment_report)
        self.create_button("Logout", self.logout)

    # =========================
    # STUDENT DASHBOARD
    # =========================
    def show_student_dashboard(self):
        self.clear_frame()
        self.create_title("Student Dashboard")

        self.create_button("View My Profile", self.view_my_profile)
        self.create_button("View My Grades", self.view_my_grades)
        self.create_button("View My GPA", self.view_my_gpa)
        self.create_button("Logout", self.logout)

    # =========================
    # COORDINATOR DASHBOARD
    # =========================
    def show_coordinator_dashboard(self):
        self.clear_frame()
        self.create_title("Academic Coordinator Dashboard")

        self.create_button("View Top Students", self.view_top_students)
        self.create_button("View Subject Performance", self.view_subject_performance)
        self.create_button("View Teacher Load Summary", self.view_teacher_load_summary)
        self.create_button("View Teacher Assignment Report", self.view_teacher_assignment_report)
        self.create_button("View Class Performance Stats", self.view_class_performance_stats)
        self.create_button("View Class Schedule", self.view_class_schedule)
        self.create_button("Logout", self.logout)

    # =========================
    # ADMIN / TEACHER FORMS
    # =========================
    def show_add_student_form(self):
        self.clear_frame()
        self.create_title("Add New Student")

        form = tk.Frame(self.main_frame)
        form.pack(pady=10)

        labels = ["StudentID", "StudentName", "BirthDate (YYYY-MM-DD)", "ClassID", "Address"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0, padx=10, pady=8, sticky="e")
            entry = tk.Entry(form, width=35)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[label] = entry

        def submit():
            try:
                student_id = int(entries["StudentID"].get())
                student_name = entries["StudentName"].get()
                birth_date = entries["BirthDate (YYYY-MM-DD)"].get()
                class_id = int(entries["ClassID"].get())
                address = entries["Address"].get()

                sql = """
                    INSERT INTO Students (StudentID, StudentName, BirthDate, ClassID, Address)
                    VALUES (%s, %s, %s, %s, %s)
                """

                ok = self.execute_query(sql, (student_id, student_name, birth_date, class_id, address))

                if ok:
                    messagebox.showinfo("Success", "Student added successfully.")
                    self.show_dashboard()

            except ValueError:
                messagebox.showerror("Input Error", "StudentID and ClassID must be numbers.")

        tk.Button(form, text="Submit", width=20, command=submit).grid(row=len(labels), column=0, columnspan=2, pady=15)
        tk.Button(form, text="Back", width=20, command=self.show_dashboard).grid(row=len(labels)+1, column=0, columnspan=2)

    def show_update_student_form(self):
        self.clear_frame()
        self.create_title("Update Student Address")

        form = tk.Frame(self.main_frame)
        form.pack(pady=10)

        tk.Label(form, text="StudentID").grid(row=0, column=0, padx=10, pady=8)
        tk.Label(form, text="New Address").grid(row=1, column=0, padx=10, pady=8)

        student_id_entry = tk.Entry(form, width=35)
        address_entry = tk.Entry(form, width=35)

        student_id_entry.grid(row=0, column=1, padx=10, pady=8)
        address_entry.grid(row=1, column=1, padx=10, pady=8)

        def submit():
            try:
                student_id = int(student_id_entry.get())
                new_address = address_entry.get()

                sql = """
                    UPDATE Students
                    SET Address = %s
                    WHERE StudentID = %s
                """

                ok = self.execute_query(sql, (new_address, student_id))

                if ok:
                    messagebox.showinfo("Success", "Student address updated successfully.")
                    self.show_dashboard()

            except ValueError:
                messagebox.showerror("Input Error", "StudentID must be a number.")

        tk.Button(form, text="Submit", width=20, command=submit).grid(row=2, column=0, columnspan=2, pady=15)
        tk.Button(form, text="Back", width=20, command=self.show_dashboard).grid(row=3, column=0, columnspan=2)

    def show_enter_grade_form(self):
        self.clear_frame()
        self.create_title("Enter New Grade")

        form = tk.Frame(self.main_frame)
        form.pack(pady=10)

        labels = ["GradeID", "StudentID", "SubjectID", "Score"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0, padx=10, pady=8, sticky="e")
            entry = tk.Entry(form, width=35)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[label] = entry

        def submit():
            try:
                grade_id = int(entries["GradeID"].get())
                student_id = int(entries["StudentID"].get())
                subject_id = int(entries["SubjectID"].get())
                score = float(entries["Score"].get())

                sql = """
                    INSERT INTO Grades (GradeID, StudentID, SubjectID, Score)
                    VALUES (%s, %s, %s, %s)
                """

                ok = self.execute_query(sql, (grade_id, student_id, subject_id, score))

                if ok:
                    messagebox.showinfo("Success", "Grade entered successfully.")
                    self.show_dashboard()

            except ValueError:
                messagebox.showerror("Input Error", "GradeID, StudentID, SubjectID and Score must be valid numbers.")

        tk.Button(form, text="Submit", width=20, command=submit).grid(row=len(labels), column=0, columnspan=2, pady=15)
        tk.Button(form, text="Back", width=20, command=self.show_dashboard).grid(row=len(labels)+1, column=0, columnspan=2)

    def show_class_roster_form(self):
        self.clear_frame()
        self.create_title("View Class Roster")

        form = tk.Frame(self.main_frame)
        form.pack(pady=10)

        tk.Label(form, text="ClassName").grid(row=0, column=0, padx=10, pady=8)

        class_name_entry = tk.Entry(form, width=35)
        class_name_entry.grid(row=0, column=1, padx=10, pady=8)

        def submit():
            class_name = class_name_entry.get().strip()

            sql = """
                SELECT ClassID, ClassName, StudentID, StudentName, BirthDate, Address
                FROM vw_class_roster
                WHERE ClassName = %s
            """

            rows = self.fetch_all(sql, (class_name,))
            columns = ("ClassID", "ClassName", "StudentID", "StudentName", "BirthDate", "Address")
            self.show_table("Class Roster", columns, rows)

        tk.Button(form, text="Search", width=20, command=submit).grid(row=1, column=0, columnspan=2, pady=15)
        tk.Button(form, text="Back", width=20, command=self.show_dashboard).grid(row=2, column=0, columnspan=2)

    # =========================
    # REPORTS
    # =========================
    def view_top_students(self):
        sql = """
            SELECT StudentID, StudentName, ClassName, AverageScore
            FROM vw_top_students
            LIMIT 10
        """

        rows = self.fetch_all(sql)
        columns = ("StudentID", "StudentName", "ClassName", "AverageScore")
        self.show_table("Top Students", columns, rows)

    def view_subject_performance(self):
        sql = """
            SELECT SubjectID, SubjectName, NumberOfGrades, AverageScore, MinScore, MaxScore
            FROM vw_subject_performance
        """

        rows = self.fetch_all(sql)
        columns = ("SubjectID", "SubjectName", "NumberOfGrades", "AverageScore", "MinScore", "MaxScore")
        self.show_table("Subject Performance", columns, rows)

    def view_teacher_load_summary(self):
        sql = """
            SELECT TeacherID, TeacherName, Subject, NumberOfClasses
            FROM vw_teacher_load_summary
        """

        rows = self.fetch_all(sql)
        columns = ("TeacherID", "TeacherName", "Subject", "NumberOfClasses")
        self.show_table("Teacher Load Summary", columns, rows)

    def view_class_performance_stats(self):
        sql = """
            SELECT c.ClassID, c.ClassName, cps.AverageScore, cps.LastUpdated
            FROM ClassPerformanceStats cps
            JOIN Classes c ON cps.ClassID = c.ClassID
            ORDER BY cps.AverageScore DESC
        """

        rows = self.fetch_all(sql)
        columns = ("ClassID", "ClassName", "AverageScore", "LastUpdated")
        self.show_table("Class Performance Stats", columns, rows)

    # =========================
    # STUDENT FUNCTIONS
    # =========================
    def view_my_profile(self):
        student_id = self.current_user["StudentID"]

        if student_id is None:
            messagebox.showerror("Account Error", "This account is not linked to a student.")
            return

        sql = """
            SELECT s.StudentID, s.StudentName, s.BirthDate, c.ClassName, s.Address
            FROM Students s
            JOIN Classes c ON s.ClassID = c.ClassID
            WHERE s.StudentID = %s
        """

        rows = self.fetch_all(sql, (student_id,))
        columns = ("StudentID", "StudentName", "BirthDate", "ClassName", "Address")
        self.show_table("My Profile", columns, rows)

    def view_my_grades(self):
        student_id = self.current_user["StudentID"]

        if student_id is None:
            messagebox.showerror("Account Error", "This account is not linked to a student.")
            return

        sql = """
            SELECT sub.SubjectName, g.Score
            FROM Grades g
            JOIN Subjects sub ON g.SubjectID = sub.SubjectID
            WHERE g.StudentID = %s
            ORDER BY sub.SubjectName
        """

        rows = self.fetch_all(sql, (student_id,))
        columns = ("SubjectName", "Score")
        self.show_table("My Grades", columns, rows)

    def view_my_gpa(self):
        student_id = self.current_user["StudentID"]

        if student_id is None:
            messagebox.showerror("Account Error", "This account is not linked to a student.")
            return

        sql = """
            SELECT StudentID, StudentName, fn_student_gpa(StudentID) AS GPA
            FROM Students
            WHERE StudentID = %s
        """

        rows = self.fetch_all(sql, (student_id,))
        columns = ("StudentID", "StudentName", "GPA")
        self.show_table("My GPA", columns, rows)

    def show_add_subject_form(self):
     self.clear_frame()
     self.create_title("Add New Subject")

     form = tk.Frame(self.main_frame)
     form.pack(pady=10)

     tk.Label(form, text="SubjectID").grid(row=0, column=0, padx=10, pady=8, sticky="e")
     tk.Label(form, text="SubjectName").grid(row=1, column=0, padx=10, pady=8, sticky="e")

     subject_id_entry = tk.Entry(form, width=35)
     subject_name_entry = tk.Entry(form, width=35)

     subject_id_entry.grid(row=0, column=1, padx=10, pady=8)
     subject_name_entry.grid(row=1, column=1, padx=10, pady=8)

     def submit():
        try:
            subject_id = int(subject_id_entry.get())
            subject_name = subject_name_entry.get().strip()

            sql = """
                INSERT INTO Subjects (SubjectID, SubjectName)
                VALUES (%s, %s)
            """

            ok = self.execute_query(sql, (subject_id, subject_name))

            if ok:
                messagebox.showinfo("Success", "Subject added successfully.")
                self.show_dashboard()

        except ValueError:
            messagebox.showerror("Input Error", "SubjectID must be a number.")

     tk.Button(form, text="Submit", width=20, command=submit).grid(row=2, column=0, columnspan=2, pady=15)
     tk.Button(form, text="Back", width=20, command=self.show_dashboard).grid(row=3, column=0, columnspan=2)

    def show_assign_subject_to_class_form(self):
     self.clear_frame()
     self.create_title("Assign Subject to Class")

     form = tk.Frame(self.main_frame)
     form.pack(pady=10)

     tk.Label(form, text="ClassID").grid(row=0, column=0, padx=10, pady=8, sticky="e")
     tk.Label(form, text="SubjectID").grid(row=1, column=0, padx=10, pady=8, sticky="e")

     class_id_entry = tk.Entry(form, width=35)
     subject_id_entry = tk.Entry(form, width=35)

     class_id_entry.grid(row=0, column=1, padx=10, pady=8)
     subject_id_entry.grid(row=1, column=1, padx=10, pady=8)

     def submit_assignment():
        class_id = class_id_entry.get().strip()
        subject_id = subject_id_entry.get().strip()

        if not class_id or not subject_id:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        if not class_id.isdigit():
            messagebox.showerror("Input Error", "ClassID must be a number.")
            return

        if not subject_id.isdigit():
            messagebox.showerror("Input Error", "SubjectID must be a number.")
            return

        try:
            conn = get_connection()

            if conn is None:
                messagebox.showerror("Connection Error", "Cannot connect to database.")
                return

            cursor = conn.cursor()

            # Check ClassID exists
            cursor.execute(
                "SELECT COUNT(*) FROM Classes WHERE ClassID = %s",
                (int(class_id),)
            )
            class_exists = cursor.fetchone()[0]

            if class_exists == 0:
                messagebox.showerror(
                    "Input Error",
                    f"ClassID {class_id} does not exist. Please create this class first."
                )
                cursor.close()
                conn.close()
                return

            # Check SubjectID exists
            cursor.execute(
                "SELECT COUNT(*) FROM Subjects WHERE SubjectID = %s",
                (int(subject_id),)
            )
            subject_exists = cursor.fetchone()[0]

            if subject_exists == 0:
                messagebox.showerror(
                    "Input Error",
                    f"SubjectID {subject_id} does not exist. Please create this subject first."
                )
                cursor.close()
                conn.close()
                return

            # Insert into ClassSubjects
            cursor.execute(
                """
                INSERT INTO ClassSubjects (ClassID, SubjectID)
                VALUES (%s, %s)
                """,
                (int(class_id), int(subject_id))
            )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Subject assigned to class successfully.")

            class_id_entry.delete(0, tk.END)
            subject_id_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

     tk.Button(
        self.main_frame,
        text="Assign Subject",
        width=20,
        command=submit_assignment
     ).pack(pady=10)

     tk.Button(
        self.main_frame,
        text="Back to Dashboard",
        width=20,
        command=self.show_admin_dashboard
     ).pack(pady=5)
    
    def show_all_tables(self):
     self.clear_frame()
     self.create_title("View All Tables")

     tables = [
        "Subjects",
        "Teachers",
        "Classes",
        "Students",
        "ClassSubjects",
        "Grades",
        "ClassSchedules",
        "Users",
        "ClassPerformanceStats"
     ]

     button_frame = tk.Frame(self.main_frame)
     button_frame.pack(pady=10)

     for table_name in tables:
        tk.Button(
            button_frame,
            text=f"View {table_name}",
            width=30,
            command=lambda t=table_name: self.view_table_data(t)
        ).pack(pady=5)

     tk.Button(
        self.main_frame,
        text="Back to Dashboard",
        width=30,
        command=self.show_admin_dashboard
     ).pack(pady=15)

    def show_create_class_form(self):
     self.clear_frame()
     self.create_title("Create New Class")

     form = tk.Frame(self.main_frame)
     form.pack(pady=10)

     tk.Label(form, text="ClassID").grid(row=0, column=0, padx=10, pady=8, sticky="e")
     tk.Label(form, text="ClassName").grid(row=1, column=0, padx=10, pady=8, sticky="e")
     tk.Label(form, text="TeacherID").grid(row=2, column=0, padx=10, pady=8, sticky="e")

     class_id_entry = tk.Entry(form, width=35)
     class_name_entry = tk.Entry(form, width=35)
     teacher_id_entry = tk.Entry(form, width=35)

     class_id_entry.grid(row=0, column=1, padx=10, pady=8)
     class_name_entry.grid(row=1, column=1, padx=10, pady=8)
     teacher_id_entry.grid(row=2, column=1, padx=10, pady=8)

     def submit_class():
        class_id = class_id_entry.get().strip()
        class_name = class_name_entry.get().strip()
        teacher_id = teacher_id_entry.get().strip()

        if not class_id or not class_name or not teacher_id:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        if not class_id.isdigit():
            messagebox.showerror("Input Error", "ClassID must be a number.")
            return

        if not teacher_id.isdigit():
            messagebox.showerror("Input Error", "TeacherID must be a number.")
            return

        try:
            conn = get_connection()
            if conn is None:
                messagebox.showerror("Connection Error", "Cannot connect to database.")
                return
            cursor = conn.cursor()

            # Check whether TeacherID exists
            cursor.execute(
                "SELECT COUNT(*) FROM Teachers WHERE TeacherID = %s",
                (int(teacher_id),)
            )
            teacher_exists = cursor.fetchone()[0]

            if teacher_exists == 0:
                messagebox.showerror(
                    "Input Error",
                    f"TeacherID {teacher_id} does not exist. Please use an existing TeacherID."
                )
                cursor.close()
                conn.close()
                return

            # Insert new class
            query = """
                INSERT INTO Classes (ClassID, ClassName, TeacherID)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    int(class_id),
                    class_name,
                    int(teacher_id)
                )
            )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "New class created successfully.")

            class_id_entry.delete(0, tk.END)
            class_name_entry.delete(0, tk.END)
            teacher_id_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

     tk.Button(
        self.main_frame,
        text="Create Class",
        width=20,
        command=submit_class
      ).pack(pady=10)

     tk.Button(
        self.main_frame,
        text="Back to Dashboard",
        width=20,
        command=self.show_admin_dashboard
      ).pack(pady=5)
    def submit():
        try:
            class_id = int(class_id_entry.get())
            class_name = class_name_entry.get().strip()
            teacher_id = int(teacher_id_entry.get())

            sql = """
                INSERT INTO Classes (ClassID, ClassName, TeacherID)
                VALUES (%s, %s, %s)
            """

            ok = self.execute_query(sql, (class_id, class_name, teacher_id))

            if ok:
                messagebox.showinfo("Success", "Class created successfully.")
                self.show_dashboard()

        except ValueError:
            messagebox.showerror("Input Error", "ClassID and TeacherID must be numbers.")

        tk.Button(form, text="Submit", width=20, command=submit).grid(row=3, column=0, columnspan=2, pady=15)
        tk.Button(form, text="Back", width=20, command=self.show_dashboard).grid(row=4, column=0, columnspan=2)

    def show_create_schedule_form(self):
     self.clear_frame()
     self.create_title("Create Class Schedule")

     form = tk.Frame(self.main_frame)
     form.pack(pady=10)

     labels = [
        "ScheduleID",
        "ClassID",
        "SubjectID",
        "TeacherID",
        "DayOfWeek",
        "StartTime (HH:MM:SS)",
        "EndTime (HH:MM:SS)",
        "Room"
    ]

     entries = {}

     for i, label in enumerate(labels):
        tk.Label(form, text=label).grid(row=i, column=0, padx=10, pady=6, sticky="e")
        entry = tk.Entry(form, width=35)
        entry.grid(row=i, column=1, padx=10, pady=6)
        entries[label] = entry

     def submit():
        try:
            schedule_id = int(entries["ScheduleID"].get())
            class_id = int(entries["ClassID"].get())
            subject_id = int(entries["SubjectID"].get())
            teacher_id = int(entries["TeacherID"].get())
            day_of_week = entries["DayOfWeek"].get().strip()
            start_time = entries["StartTime (HH:MM:SS)"].get().strip()
            end_time = entries["EndTime (HH:MM:SS)"].get().strip()
            room = entries["Room"].get().strip()

            sql = """
                INSERT INTO ClassSchedules 
                (ScheduleID, ClassID, SubjectID, TeacherID, DayOfWeek, StartTime, EndTime, Room)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            ok = self.execute_query(
                sql,
                (schedule_id, class_id, subject_id, teacher_id, day_of_week, start_time, end_time, room)
            )

            if ok:
                messagebox.showinfo("Success", "Class schedule created successfully.")
                self.show_dashboard()

        except ValueError:
            messagebox.showerror("Input Error", "ScheduleID, ClassID, SubjectID, and TeacherID must be numbers.")

     tk.Button(form, text="Submit", width=20, command=submit).grid(row=len(labels), column=0, columnspan=2, pady=15)
     tk.Button(form, text="Back", width=20, command=self.show_dashboard).grid(row=len(labels)+1, column=0, columnspan=2)

    def view_class_schedule(self):
     sql = """
        SELECT ScheduleID, ClassName, SubjectName, TeacherName, DayOfWeek, StartTime, EndTime, Room
        FROM vw_class_schedule
     """

     rows = self.fetch_all(sql)

     columns = (
        "ScheduleID",
        "ClassName",
        "SubjectName",
        "TeacherName",
        "DayOfWeek",
        "StartTime",
        "EndTime",
        "Room"
    )

     self.show_table("Class Schedule", columns, rows)

    def view_teacher_assignment_report(self):
     sql = """
        SELECT TeacherID, TeacherName, Specialization, ClassName, SubjectName, DayOfWeek, StartTime, EndTime, Room
        FROM vw_teacher_assignment_report
     """

     rows = self.fetch_all(sql)

     columns = (
        "TeacherID",
        "TeacherName",
        "Specialization",
        "ClassName",
        "SubjectName",
        "DayOfWeek",
        "StartTime",
        "EndTime",
        "Room"
     )

     self.show_table("Teacher Assignment Report", columns, rows)

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolManagementApp(root)
    root.mainloop()