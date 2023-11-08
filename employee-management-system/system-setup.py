# File to setup database required for employee management system

import mysql
import mysql.connector
from time import sleep
import bcrypt

# Attempts to connect to mysql
print("Enter MySQL connection password:")
dbpassword = input()
try:
    print("Connecting to MySQL...")
    conn = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = dbpassword,
    )
except mysql.connector.Error as err:
    # Displays error if connection unsuccessful
    print("Error has occured connecting to mysql.")
    print(err)
    input()
    exit()
else:
    cursor = conn.cursor()
    print("MySQL connection successful.")

# Checks for existing database
sql_query = "SHOW DATABASES LIKE 'employee_management'"
cursor.execute(sql_query)
db = cursor.fetchone()
if db == None:
    dbexists = False
else:
    dbexists = True

# If database doesn't exist, create it
if dbexists == True:
    print("Error: Database already exists")
    input()
    exit()
elif dbexists == False:
    cursor.reset()
    try:
        sql_query = "CREATE DATABASE employee_management; USE employee_management; CREATE TABLE employees (employeeid INT NOT NULL PRIMARY KEY AUTO_INCREMENT, fullname varchar(255) NOT NULL, age INT NOT NULL, position varchar(255) NOT NULL, salary INT NOT NULL); CREATE TABLE system_logins (userid INT NOT NULL PRIMARY KEY AUTO_INCREMENT, username varchar(255) NOT NULL, passwordhash varchar(255) NOT NULL, permissionlevel INT NOT NULL)"
        cursor.execute(sql_query)
    except:
        print("Error: Error creating Database")
        input()
        exit()
    else:
        conn.close()
        try:
            print("Connecting to Database...")
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
            input()
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
                sleep(6)
                exit()
            
