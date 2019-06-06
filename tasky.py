 # -*- coding: utf-8 -*-
import re
import requests
import datetime
import sqlite3 
import os
import threading
import time
import sys
from mylist import mylist
from lxml import html


db = 'results.db'
schema_filename = 'schema.sql'

checklist = []
checklist = mylist

db_exists = not os.path.exists(db)
connection = sqlite3.connect(db,  check_same_thread=False)

def main():  
    db_start = database(db) #Calls the function to check for the database.
    # starts the threading and let's it run till the program is termianted with crtl+c
    try:
        thread = threading.Thread(target=running, daemon=True)
        thread.start()
        while True:
            thread.join(1)     
    except KeyboardInterrupt:
        print ("Ctrl+C pressed...")
        sys.exit(1)
        
#calls the check function until the program is terminated every X seconds
def running():
    try:
        while True:
            check_list = check(db)
            time.sleep(20)
    except KeyboardInterrupt:
        print ("Ctrl+C pressed...")
        sys.exit(1)
        
    
#Checks if the database exists. If not it creates the database.
def database(db):
    try:
        if db_exists:
            print ('DB does not exist')
            with open(schema_filename, 'rt') as file:
                schema = file.read()
                connection.executescript(schema)
        else:
            print ('DB exists')
    except:
        pass
        


#Checks all URLs given and writes the results into the database
def check(db):  
    # Check for the URLs and combine them with the regex if given. Try to request those URLS.
    for item in checklist:
        try:
            #check if there is an regex in the list behind the url or not
            if len(item) == 1:
                url = item[0]
                regexp = None    
            else:
                url = item[0]
                regexp = item[1]
            try:
                #tries if the url responds
                r = requests.get(url)
                cont = r.text
                time = datetime.datetime.now()
                time2 = time.strftime("%Y-%m-%d %H:%M:%S") #time 2 formats the date to a normal datestamp: Year Month Day Hour:Minute:Second
                response = r.elapsed.total_seconds() #response geives the response time of the query
                status = r.status_code #status code is to check if the homepage is valid (200) or any other code such as 404
                # check if status is a valid homepage else give the code as an error
                if status == 200:
                    error = str("no error")
                    if regexp != None:
                        matching = re.findall(regexp, cont) #Checks the regex and tells how many matches were found
                        number_matching = len(matching)
                    else:
                        number_matching = 0 #if no regex number of regex matches is automatically 0
                #if the status is anything except 200 it saves the code as an error        
                else:
                    error = str(status)
                    number_matching = 0
                succesfull = 1                          #sucessfull is a binary. 1 = yes and 0 = no if the check was succesfull although an error (like 404) was received it still counts as a succesfull check    
                res = connection.execute("INSERT INTO check_results (url, check_time, response_time, error, succesfull, regex_matches) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"%(url, time2, response, error, succesfull, number_matching))
                connection.commit()
            # If an error appears put the error and the data into the database 
            except Exception as e :
                time = datetime.datetime.now()
                time2 = time.strftime("%Y-%m-%d %H:%M:%S")
                response = r.elapsed.total_seconds()
                succesfull = 0
                number_matching = 0
                error = str(e).replace("'","\"")
                resu = connection.execute("INSERT INTO check_results (url, check_time, response_time, error, succesfull, regex_matches) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"%(url, time2, response, error, succesfull, number_matching))
                connection.commit()
        #if everything fails, save it as a fail and save the error too for possible checkup, then continue        
        except Exception as e :
            time = datetime.datetime.now()
            time2 = time.strftime("%Y-%m-%d %H:%M:%S")
            response = r.elapsed.total_seconds()
            succesfull = 0
            number_matching = 0
            error = str(e).replace("'","\"")
            resu = connection.execute("INSERT INTO check_results (url, check_time, response_time, error, succesfull, regex_matches) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"%(url, time2, response, error, succesfull, number_matching))
            connection.commit()

            
#calling the main function
main()
