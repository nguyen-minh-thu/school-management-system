import mysql.connector
from mysql.connector import Error


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="PASSWORD",
            database="school_management"
        )
        return connection
    except Error as e:
        print("Database connection failed:", e)
        return None
