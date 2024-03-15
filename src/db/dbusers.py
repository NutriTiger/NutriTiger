import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import pytz
from dbfunctions import connectmongo
from dbnutrition import find_one_nutrition
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
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]

        eastern_time = datetime.now(pytz.timezone('US/Eastern'))
        today = eastern_time.date()

        # create new document for this user
        user_document = {"_id": bson.ObjectId(), 
                        "name" : name, 
                        "netid" : netid, 
                        "join_date" : today,
                        "current_entry" : today,
                        "bday" : bday, 
                        "caloricgoal" : cal,
                        "cal_his" : [0],
                        "carb_his" : [0],
                        "fat_his" : [0],
                        "prot_his" : [0],
                        "daily" : [],
                        "serving" : [],
                        }

        # insert document into the collection
        try:
            users_collection.insert_one(user_document)
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
        else:
            print(f"Created new user with netid: {netid}.")

        return

# Update user history and "check in" for today's login
def userlogin(netid):
    this_user = finduser(netid)
    if this_user is None:
        return
    
    # figure out today
    eastern_time = datetime.now(pytz.timezone('US/Eastern'))
    today = eastern_time.date()

    # calculate difference between today and last entry
    last_entry = this_user["current_entry"]
    diff = (today - last_entry).days

    # if it's the same day, no updates necessary
    if (diff == 0):
        return
    
    # update fields
    cal_his = this_user["cal_his"]
    carb_his = this_user["carb_his"]
    fat_his = this_user["fat_his"]
    prot_his = this_user["prot_his"]

    for i in range(diff):
        cal_his.insert(0, 0)
        carb_his.append(0, 0)
        fat_his.append(0, 0)
        prot_his.append(0, 0)

    # connect to database and update
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]

        who = {"netid": netid}
        update = {
            "$set": {
                "daily": [],
                "serving": [],
                "cal_his" = cal_his
                "carb_his" = carb_his
                "fat_his" = fat_his
                "prot_his" = prot_his
            }
        }
        updated = users_collection.find_one_and_update(who, update, new=True)
        except pymongo.errors.OperationFailure:
                print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
                sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
                print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
                sys.exit(1)
        if updated is None:
            print(f"Database has changed while running. There does not exists a document with netid : {netid}")
            return

# Update user's calorie goal
def updategoal(netid, cal):
    this_user = finduser(netid)
    if this_user is None:
        return
    
    # connect to database
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        try:
            updated = users_collection.find_one_and_update({"netid": netid}, {"$set" : {"caloricgoal" : cal}}, new=True)
        except pymongo.errors.OperationFailure:
                print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
                sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
                print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
                sys.exit(1)
        if updated is None:
            print(f"Database has changed while running. There does not exists a document with netid : {netid}")
        return

# INSIDE UPDATEDCONSUMED: organize macro/calorie count:
def __updatenutrition__(netid, entry):
    this_user = finduser(netid)
    if this_user is None:
        return
    
    entry_cal = 0
    entry_carb = 0
    entry_fat = 0
    entry_prot = 0

    for recipeid, serving in zip(entry[0], entry[1]):
        nut = find_one_nutrition(recipeid)
        if nut is None:
            print(f"Could not find recipe with recipid: {recipeid}")
            return
        entry_cal = entry_cal + nut["calories"]*serving
        entry_carb = entry_carb + nut["carbs"]*serving
        entry_fat = entry_fat + nut["fats"]*serving
        entry_prot = entry_prot + nut["protein"]*serving
    
    return

# Update user's consumed good: add to daily plate
# Note: Entry is an array of two arrays: one containing the recipeid's and one containing the serving sizes
def addconsumed(netid, entry):
    this_user = finduser(netid)
    if this_user is None:
        return
    
    daily = this_user["daily"]
    servings = this_user["servings"]

    for recipe in entry[0]:
        daily.append(recipe)
    for serving in entry[1]:
        servings.append(serving)

    updated_nutrition = __updatenutrition__(netid, entry)

    
    return

# Update user's consumed good: delete entry from daily plate
def deleteconsumed():
    return

# Retrive user's profile (including name/netid, goals, consumed)
def finduser(netid):
    # connect to database
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        try:
            this_user = users_collection.find_one({"netid": netid})
        except pymongo.errors.OperationFailure:
                print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
                sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
                print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
                sys.exit(1)

        if this_user is None:
            print(f"There does not exists a document with netid : {netid}")
        return this_user

# delete user's data entries
def deleteuser():
    return

# USED FOR TESTING FOR NOW 
def main(): 
    newuser("Jewel", "jm0278", datetime(2004, 3, 9).date(), 2000)
    updategoal("jm0278", 2500)
    return

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()