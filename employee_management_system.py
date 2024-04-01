# Importing modules
from time import sleep
import pymongo
from os import getenv
from dotenv import load_dotenv
import bcrypt
from secrets import compare_digest
# Initialize .env file
load_dotenv()

# Permission levels
    # 1 - Read
    # 2 - Read and edit
    # 3 - Read, edit, manage system users
    # 4 - Admin user (All perms from below, and can edit all system users including other admin users, rank level 3 cannot)
    # 5 - root user

# Attempts MongoDB connection
try:
    url = getenv("MONGOKEY")
    client = pymongo.MongoClient(url)
    db = client["ManagementSystem"]
    employees = db["employees"]
    logins = db["logins"]
except:
    print("Error occured connecting to database.")
else:
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
        print("Please enter your username:")
        username = input().lower()
        print("Please enter your password:")
        password = input()
        # Fetches hashed password and salt from database
        query = { "username": username }
        document = logins.find_one(query,{ "password": 1, "permissionlevel": 1})
        # Checks if username is valid, if not returns access denied
        try:
            fetchedhashed = document["password"]
        except:
            print("Access Denied.")
            failurecounter = failurecounter + 1
        else:
            hashedpassword = rehashpassword(password, fetchedhashed)
            # If password is correct, grant access and return session details, else deny access
            if compare_digest(fetchedhashed, hashedpassword):
                print("Access granted. \nLogged in as %s" % (username))
                sleep(0.8)
                loggedin = True
                permissionlevel = document["permissionlevel"]
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
    query = { "fullname": fullname }
    if employees.find_one(query) != None:
        print("Error: Employee already exists")
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
            query = { "fullname": fullname, "age": age, "position": position, "salary": salary }
            employees.insert_one(query)
        except:
            print("Error occured adding employee")
            return()
        else:
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
            name = input().lower()
            query = { "fullname": name }
            try:
                userdetails = employees.find_one(query)
                employeeid = userdetails["employeeId"]
                fullname = userdetails["fullname"]
                age = userdetails["age"]
                position = userdetails["position"]
                salary = userdetails["salary"]
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
            Records = []
            print("Enter position of employees:")
            position = input().lower()
            query = { "position": position }
            for x in employees.find({"position":position}):
                Records.append(x)
            Noofrecords = len(Records)
            if Noofrecords > 0:
                print(str(Noofrecords) + " Records Found")
                print("Enter any key to see the first record")
                input()
                for i in range(Noofrecords):
                    Currentrecord = Records[i]
                    print("Record " + str(i+1) + " of " + str(Noofrecords))
                    sleep(0.2)
                    print("Employee ID: " + str(Currentrecord["employeeId"]))
                    print("Name: " + str(Currentrecord["fullname"]))
                    print("Age: " + str(Currentrecord["age"]))
                    print("Position: " + str(Currentrecord["position"]))
                    print("Salary: " + str(Currentrecord["salary"]))
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
    query = { "employeeId": employeeid }
    newvalues = { "$set": { detailToUpdate: newInfo } }
    try:
        employees.update_one(query, newvalues)
    except:
        print("Error occured")
        return(False)
    else:
        return(True)

# Allows user to edit records
def editrecords():
    print("Please enter the employee id of the employee whose record you would like to edit")
    print("Type \"Back\" to return to menu.")
    employeeid = str(input().lower())
    query = { "employeeId": employeeid }
    document = employees.find_one(query)
    if employeeid == "back":
        sleep(0.2)
        return()
    elif document == None:
        print("No record found.")
        sleep(0.5)
        return()
    employeename = document["fullname"]
    age = str(document["age"])
    position = document["position"]
    salary = str(document["salary"])
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
    query = { "fullname": employeeName }
    if employees.find_one(query) == None:
        print("No record found.")
        sleep(0.5)
        return()
    print("You are about to delete the employee record for " + employeeName + ". To confirm, please type \"Confirm\"")
    if input().lower() == "confirm":
        query = { "fullname": employeeName }
        try:
            employees.delete_one(query)
        except:
            print("Error deleting record.")
        else:
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
        print("\nEmployee Management System v2.0.0")
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
            exit()
        else:
            print("Invalid input. Please try again.")




