import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def admin(name, username, password):
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            database=os.getenv('MYSQL_DB'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO admin (name, username, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, username, password))
            connection.commit()
            print("Admin data inserted successfully")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    name = "Admin BSI Bengkalis"
    username = "admin-bsi-bks"
    password = "admin@bsi-bks"
    admin(name, username, password)
