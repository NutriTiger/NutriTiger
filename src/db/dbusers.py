import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from dbfunctions import connectmongo
import bson
import ssl
import os
import sys
#----------------------------------------------------------------------
# Contributors:
# Jewel Merriman and Oyu Enkhbold
#
# Based off of atlas starter packet: 
# https://github.com/mongodb-university/atlas_starter_python/blob/master/atlas-starter.py
#----------------------------------------------------------------------

# Create new user profile: include calorie count, personal info
def newuser(name, netid, bday, cal):
    # connect to database
    db = connectmongo()

    # use a collection named "users"
    users_collection = db["users"]

    # create new document for this user
    user_document = {"_id": bson.ObjectId(), 
                    "name" : name, 
                    "netid" : netid, 
                    "join_date" : datetime.now(),
                    "current_entry" : datetime.now(),
                    "bday" : bday, 
                    "caloricgoal" : cal,
                    "cal_his" : [0],
                    "carb_his" : [0],
                    "fat_his" : [0],
                    "prot_his" : [0],
                    "daily" : [0],
                    "serving" : [0],
                    }

    # insert document into the collection
    try:
        users_collection.insert_one(user_document)
    except pymongo.errors.OperationFailure:
        print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
        sys.exit(1)
    else:
        print(f"Created new user with netid: {netid}.")
    
    return

# Update user's calorie goal
def updategoal(netid, cal):
    # connect to database
    db = connectmongo()

    # use a collection named "users"
    users_collection = db["users"]

    # find the document for this user and update if it exists
    this_user = users_collection.find_one_and_update({"netid": netid}, {"$set" : {"caloricgoal" : cal}}, new=True)
    if this_user is not None:
        print(f"The user with netid {netid} now has a caloric goal of {cal}")
    else:
        print(f"There does not exists a document with netid : {netid}")
    return

# INSIDE UPDATEDCONSUMED: organize macro/calorie count:
def __updatenutrition__():
    return

# Update user's consumed good: add to daily plate
def addconsumed():
    return

# Update user's consumed good: delete entry from daily plate
def deleteconsumed():
    return

# Retrive user's profile (including name/netid, goals, consumed)
def finduser():
    return

# delete user's data entries
def deleteuser():
    return

# USED FOR TESTING FOR NOW 
def main(): 
    return
    

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()