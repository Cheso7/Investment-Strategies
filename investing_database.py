import mysql.connector

from mysql.connector import Error

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try: 
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            passwd = user_password
        )
        print("MySQL Database Connection Successful")
    except Error as err:
        print(f"Error: '{err}'")     
    return connection

connection = create_server_connection("localhost", "root", "7Synzacky11!")

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")