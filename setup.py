
from time import sleep
import mysql
import mysql.connector

def databaseSetup():
    print("Database not found. Entering first time setup procedure:")
    print("Please enter MySQL password:")
    dbpassword = input()
    sleep(1)
    try:
        cursor.reset()
        sql_query = "CREATE DATABASE employee_management; USE employee_management; CREATE TABLE employees (employeeid INT NOT NULL PRIMARY KEY AUTO_INCREMENT, fullname varchar(255) NOT NULL, age INT NOT NULL, position varchar(255) NOT NULL, salary INT NOT NULL); CREATE TABLE system_logins (userid INT NOT NULL PRIMARY KEY AUTO_INCREMENT, username varchar(255) NOT NULL, passwordhash varchar(255) NOT NULL, permissionlevel INT NOT NULL)"
        cursor.execute(sql_query)
    except:
        print("Error: Error creating Database")
        input()
        exit()
    else:
        conn.close()
        try:
            print("Performing database setup...")
            conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = dbpassword,
            database = "employee_management"
                )
            conn.start_transaction(isolation_level='READ COMMITTED')
        except mysql.connector.Error as err:
            # Displays error if connection unsuccessful
            print("Error has occured connecting to database.")
            print(err)
            sleep(0.5)
            exit()
        else:
            cursor = conn.cursor()
            print("Database creation successful")
            sleep(0.3)
            # Sets up admin user for system
            print("Please enter admin user username")
            username = input().lower()
            match = False
            while not match:
                print("Please enter admin user password")
                password = input()
                print("Please re-enter admin user password")
                confirmpassword = input()
                if password == confirmpassword:
                    match = True
            # Hashes password with salt
            password = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashedpw = bcrypt.hashpw(password, salt)
            hashedpw = str(hashedpw)
            hashedpw = hashedpw.replace("'", "")
            hashedpw = hashedpw[1:]
            try:
                sql_query = "INSERT INTO system_logins (username, passwordhash, permissionlevel) VALUES ('%s', '%s', '5')" % (username, hashedpw)
                cursor.execute(sql_query)
            except mysql.connector.Error as err:
                conn.rollback()
                print("Error creating system user")
                print(err)
                input()
                exit()
            else:
                conn.commit()
                print("Admin user set up successful")
                print("System successfully set up")
                sleep(0.5)
    conn.close()