# Importing modules
from time import sleep
import mysql
import mysql.connector
import bcrypt

# Permission levels
    # 1 - Read
    # 2 - Read-write
    # 3 - 

# Enter MySQL password here
dbpassword = ""


# Attempts database connection
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
    print("Error has occured.")
    print(err)
    input()
    exit()
else:
    cursor = conn.cursor()
    print("Database connection successful.")

# Function for hashing a password
def hashpassword(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    hashed = str(hashed)
    hashed = hashed.replace("'","")
    hashed = hashed[1:]
    return(hashed)

# Function for re hashing a password with a given salt
def rehashpassword(password, salt):
    password = password.encode('utf-8')
    salt = salt.encode('utf-8')
    hashed = bcrypt.hashpw(password, salt)
    hashed = str(hashed)
    hashed = hashed.replace("'","")
    hashed = hashed[1:]
    return(hashed)

# Logs user into system
def login():
    # Initializes loggedin, passworddetails and failurecounter variables
    loggedin = False
    passworddetails = None
    failurecounter = 0
    while loggedin == False:
        # Terminates program after 5 failed logins
        if failurecounter > 4:
            print("Maximum number of attempts reached. Terminating program.")
            sleep(1)
            exit()
        # Prompts for username and password
        cursor.reset()
        print("Please enter your username:")
        username = input().lower()
        print("Please enter your password:")
        password = input()
        # Fetches hashed password and salt from database
        sql_query = "SELECT passwordhash FROM system_logins WHERE username='%s'" % (username)
        cursor.execute(sql_query)
        # Checks if username is valid, if not returns access denied
        try:
            fetchedhashed = cursor.fetchone()
            fetchedhashed = fetchedhashed[0]
        except TypeError:
            print("Access Denied.")
            failurecounter = failurecounter + 1
        else:
            hashedpassword = rehashpassword(password, fetchedhashed)
            # If password is correct, grant access and return session details, else deny access
            if hashedpassword == fetchedhashed:
                print("Access granted. \nLogged in as %s" % (username))
                sleep(0.8)
                loggedin = True
                cursor.reset()
                sql_query = "SELECT permissionlevel FROM system_logins WHERE username='%s'" % (username)
                cursor.execute(sql_query)
                permissionlevel = cursor.fetchone()
                return(loggedin, permissionlevel, username)
            else:
                print("Access Denied.")
                failurecounter = failurecounter + 1
    
def addrecords():
    print("Enter \"Back\" to return to menu.")
    print("Enter full employee name.")
    fullname = input().lower()
    if fullname == "back":
        return()
    # Fetches number of database entries for inputted name
    # Returns error if data found to avoid duplicate entries
    sql_query = "SELECT * FROM employees WHERE fullname='%s'" % (fullname)
    cursor.execute(sql_query)
    cursor.fetchone()
    if cursor.rowcount == 1:
        print("Error: Employee already exists")
        cursor.reset()
        return()
    else:
        print("Enter employee age:")
        valid = False
        while not valid:
            try:
                age = int(input())
            except ValueError:
                print("Age must be a number between 0 and 150")
            else:
                if age < 150 and age > 0:
                    valid = True
                else:
                    print("Age must be a number between 0 and 150")
        print("Enter employee's position:")
        position = input()
        print("Enter employee's salary")
        valid = False
        while not valid:
            try:
                salary = int(input())
            except ValueError:
                print("Salary must be a number above 0")
            else:
                if salary > 0:
                    valid = True
                else:
                    print("Salary must be a number above 0")
        salary = round(salary, 2)
        try:
            sql_query = "INSERT INTO employees (fullname, age, position, salary) VALUES ('%s', '%s', '%s', '%s')" % (fullname, age, position, salary)
            cursor.execute(sql_query)
        except mysql.connector.Error as err:
            conn.rollback()
            print("Error occured adding employee")
            print(err)
            return()
        else:
            conn.commit()
            print("Employee added successfully")
            sleep(0.2)
            return()
        


while True:
    print("System Locked.")
    sessiondetails = login()
    loggedin = sessiondetails[0]
    while loggedin == True:
        # Initialize permissionlevel and username of session
        permissionlevel = sessiondetails[1] # Fix error of permissionlevel not being int
        username = sessiondetails[2]
        print("\nEmployee Management System v1.0.0-alpha.2")
        print("To add records, please type 1")
        print("To exit, please type 5")
        choice = str(input())
        if choice == "1":
            sleep(0.3)
            if True: # Will add acceptance based on permission level at a future date
                addrecords()
            else:
                print("Access Denied.")
        if choice == "5":
            sleep(0.2)
            exit()



