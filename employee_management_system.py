# Importing modules
from time import sleep
import mysql
import mysql.connector
import bcrypt
from secrets import compare_digest
from setup import databaseSetup

# Permission levels
    # 1 - Read
    # 2 - Read and edit
    # 3 - Read, edit, manage system users
    # 4 - Admin user (All perms from below, and can edit all system users including other admin users, rank level 3 cannot)
    # 5 - root user

# Enter MySQL password here
dbpassword = ""

# Attempts MySQL connection
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

# Checks for existing database, if one isnt found sets one up
sql_query = "SHOW DATABASES LIKE 'employee_management'"
cursor.execute(sql_query)
db = cursor.fetchone()
if db == None:
    databaseSetup()

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
            if compare_digest(fetchedhashed, hashedpassword):
                print("Access granted. \nLogged in as %s" % (username))
                sleep(0.8)
                loggedin = True
                cursor.reset()
                sql_query = "SELECT permissionlevel FROM system_logins WHERE username='%s'" % (username)
                cursor.execute(sql_query)
                permissionlevel = cursor.fetchone()[0]
                return(loggedin, permissionlevel, username)
            else:
                print("Access Denied.")
                failurecounter = failurecounter + 1

# Allows user to add records  
def addrecords():
    print("Enter \"Back\" to return to menu.")
    print("Enter full employee name.")
    valid = False
    while not valid:
        fullname = input().lower()
        if fullname == "back":
            return()
        if type(fullname) == str:
            valid = True
        else:
            print("Invalid input. Please try again.")
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
        position = input().lower()
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

# Allows user to search through records
def searchrecords():
    while True:
        print("To search by name, enter \"Name\" \nTo search by position, enter \"Position\" \nTo go back to menu, type \"Back\"")
        choice = input().lower()
        if choice == "name":
            print("Enter name of employee:")
            cursor.reset()
            name = input().lower()
            sql_query = "SELECT * FROM employees WHERE fullname='%s'" % (name)
            cursor.execute(sql_query)
            try:
                userdetails = cursor.fetchone()
                employeeid = userdetails[0]
                fullname = userdetails[1]
                age = userdetails[2]
                position = userdetails[3]
                salary = userdetails[4]
            except:
                print("No records found")
                sleep(0.2)
                return()
            else:
                print("1 record found")
                sleep(0.2)
                print("Record 1:")
                sleep(0.2)
                print("Employee ID: " + str(employeeid))
                print("Name: " + str(fullname))
                print("Age: " + str(age))
                print("Position: " + str(position))
                print("Salary: " + str(salary))
                print("Enter any key to return to menu")
                input()
                return()
        elif choice == "position":
            print("Enter position of employees:")
            cursor.reset()
            position = input().lower()
            sql_query = "SELECT * FROM employees WHERE position='%s'" % (position)
            cursor.execute(sql_query)
            Records = cursor.fetchall()
            Noofrecords = cursor.rowcount
            if Noofrecords > 0:
                print(str(Noofrecords) + " Records Found")
                print("Enter any key to see the first record")
                input()
                for i in range(Noofrecords):
                    Currentrecord = Records[i]
                    print("Record " + str(i+1) + " of " + str(Noofrecords))
                    sleep(0.2)
                    print("Employee ID: " + str(Currentrecord[0]))
                    print("Name: " + str(Currentrecord[1]))
                    print("Age: " + str(Currentrecord[2]))
                    print("Position: " + str(Currentrecord[3]))
                    print("Salary: " + str(Currentrecord[4]))
                    if i < (Noofrecords-1):
                        print("Enter any key to see the next record")
                        input()
                    else:
                        print("Enter any key to return to menu")
                        input()
                        return()
            elif Noofrecords == 0:
                print("No records found")
                sleep(0.2)
                return()           
        elif choice == "back":
            return()

# Function to update information in a record
def updaterecords(employeeid, detailToUpdate, newInfo):
    employeeid = int(employeeid)
    sql_query = "UPDATE employees SET %s = '%s' WHERE employeeid = '%s'" % (detailToUpdate, newInfo, employeeid)
    cursor.reset()
    try:
        cursor.execute(sql_query)
    except mysql.connector.Error as err:
        conn.rollback()
        print(err)
        return(False)
    else:
        conn.commit()
        return(True)

# Allows user to edit records
def editrecords():
    print("Please enter the employee id of the employee whose record you would like to edit")
    print("Type \"Back\" to return to menu.")
    employeeid = str(input().lower())
    sql_query = "SELECT * FROM employees WHERE employeeid='%s'" % (employeeid)
    cursor.reset()
    cursor.execute(sql_query)
    details = cursor.fetchone()
    if employeeid == "back":
        sleep(0.2)
        return()
    elif cursor.rowcount == 0:
        print("No record found.")
        sleep(0.5)
        return()
    employeename = details[1]
    age = str(details[2])
    position = details[3]
    salary = str(details[4])
    print("You are editing the employee record of: "+employeename)
    while True:
        print("What would you like to update?\nFor name type 1\nFor age type 2\nFor position type 3\nFor salary type 4\nTo return to menu type \"Back\"")
        choice = str(input())
        if choice == "1":
            print("Current employee name is: "+employeename)
            print("Please enter new employee name:")
            newInfo = input().lower()
            successful = updaterecords(employeeid, "fullname", newInfo)
            if successful:
                print("Record successfully updated")
                employeename = newInfo
                sleep(0.5)
            elif not successful:
                print("Error updating record. Please try again later.")
                sleep(0.5)
        elif choice == "2":
            print("Current employee age is: "+age)
            print("Please enter new employee age:")
            newInfo = input().lower()
            successful = updaterecords(employeeid, "age", newInfo)
            if successful:
                print("Record successfully updated")
                age = str(newInfo)
                sleep(0.5)
            elif not successful:
                print("Error updating record. Please try again later.")
                sleep(0.5)
        elif choice == "3":
            print("Current employee position is: "+position)
            print("Please enter new employee position:")
            newInfo = input().lower()
            successful = updaterecords(employeeid, "position", newInfo)
            if successful:
                print("Record successfully updated")
                position = newInfo
                sleep(0.5)
            elif not successful:
                print("Error updating record. Please try again later.")
                sleep(0.5)
        elif choice == "4":
            print("Current employee salary is: "+salary)
            print("Please enter new employee salary:")
            newInfo = input().lower()
            successful = updaterecords(employeeid, "salary", newInfo)
            if successful:
                print("Record successfully updated")
                salary = str(newInfo)
                sleep(0.5)
            elif not successful:
                print("Error updating record. Please try again later.")
                sleep(0.5)
        elif choice == "back":
            sleep(0.2)
            return()
        else:
            print("Invalid input. Please try again.")
            sleep(0.3)

# Allows user to delete records
def deleterecords():
    print("Please enter the name of the employee whose record you wish to delete:")
    employeeName = input().lower()
    sql_query = "SELECT * FROM employees WHERE fullname='%s'" % (employeeName)
    cursor.reset()
    cursor.execute(sql_query)
    cursor.fetchone()
    if cursor.rowcount == 0:
        print("No record found.")
        sleep(0.5)
        return()
    print("You are about to delete the employee record for " + employeeName + ". To confirm, please type \"Confirm\"")
    cursor.reset()
    if input().lower() == "confirm":
        sql_query = "DELETE FROM employees WHERE fullname='%s'" % (employeeName)
        try:
            cursor.execute(sql_query)
        except mysql.connector.Error as err:
            conn.rollback()
            print("Error deleting record.")
            print("Error message: " + err)
        else:
            conn.commit()
            print("Record deleted successfully.")
            sleep(0.5)
            return()
    else:
        print("Action cancelled.")
        sleep(0.5)
        return()

def manageusers(isadmin):
    return()

while True:
    print("System Locked.")
    sessiondetails = login()
    loggedin = sessiondetails[0]
    while loggedin == True:
        # Initialize permissionlevel and username of session
        permissionlevel = sessiondetails[1] # Fix error of permissionlevel not being int
        username = sessiondetails[2]
        print("\nEmployee Management System v1.1.1")
        print("To add records, please type 1")
        print("To search existing records, type 2")
        print("To edit existing records, type 3")
        print("To delete existing records, type 4")
        #print("To manage system users, type 5")
        print("To exit, type 6")
        choice = str(input())
        if choice == "1":
            sleep(0.3)
            if permissionlevel > 1: # Will add acceptance based on permission level at a future date
                addrecords()
            else:
                print("Access Denied.")
        elif choice == "2":
            sleep(0.2)
            if permissionlevel > 0:
                searchrecords()
                sleep(0.2)
            else:
                print("Access Denied.")
        elif choice == "3":
            sleep(0.2)
            if permissionlevel > 1:
                editrecords()
            else:
                print("Access Denied.")
        elif choice == "4":
            sleep(0.2)
            if permissionlevel > 1:
                deleterecords()
            else:
                print("Access Denied.")
        #elif choice == "5":
        #    if permissionlevel > 2:
        #        if permissionlevel >= 4:
        #            manageusers(True)
        #        else:
        #            manageusers(False)
        #    else:
        #        print("Access Denied.")
        elif choice == "6":
            sleep(0.2)
            conn.close()
            exit()
        else:
            print("Invalid input. Please try again.")




