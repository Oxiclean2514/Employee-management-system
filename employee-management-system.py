# Importing modules
from time import sleep
import mysql
import mysql.connector

# Permission levels
    # 1 - Read
    # 2 - Read-write
    # 3 - 
# Attempts database connection
try:
    print("Connecting to Database...")
    sleep(1.2)
    conn = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "",
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


def rehashpassword(password, salt):
    import bcrypt
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
        print("Please enter your password")
        password = input()
        # Fetches hashed password and salt from database
        sql_query = "SELECT passwordhash, passwordsalt FROM system_logins WHERE username='%s'" % (username)
        cursor.execute(sql_query)
        passworddetails = cursor.fetchone()
        try:
            fetchedhashed = passworddetails[0]
            fetchedsalt = passworddetails[1] 
            hashedpassword = rehashpassword(password, fetchedsalt)
        except:
            sleep(0.5)
            print("Access Denied.")
            failurecounter = failurecounter + 1
        else:
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
    

while True:
    print("System Locked.")
    sessiondetails = login()
    loggedin = sessiondetails[0]
    while loggedin == True:
        permissionlevel = sessiondetails[1]
        username = sessiondetails[2]
        print("\nEmployee Management System v1.0.0-alpha.1")
        print("For changelog type \"changelog\"")
        input()




