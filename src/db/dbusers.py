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
        # check that this user does not already exist
        this_user = finduser(netid)
        if this_user is not None:
            print(f"A user with netid {netid} already exists.")
            return
        # create new document for this user
        db = client.db
        users_collection = db["users"]
        today = datetime.now(pytz.timezone('US/Eastern'))

        ########### FOR TESTING DATE
        #eastern_time = pytz.timezone('US/Eastern')
        #today_date = datetime(2024, 3, 14)
        #today = eastern_time.localize(today_date)

        user_document = {"_id": bson.ObjectId(), 
                        "name" : name, 
                        "netid" : netid, 
                        "bday" : bday, 
                        "caloricgoal" : cal,
                        "join_date" : today,
                        "last_login" : today,
                        "cal_his" : [0],
                        "carb_his" : [0],
                        "fat_his" : [0],
                        "prot_his" : [0],
                        "daily_rec" : [],
                        "daily_serv" : [],
                        "daily_nut" : []
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
    today = datetime.now(pytz.timezone('US/Eastern'))

    # calculate difference between today and last entry
    last_login = this_user["last_login"]
    diff = (today.date() - last_login.date()).days

    # if it's the same day, no updates necessary
    if (diff == 0):
        print("same day login")
        return

    # update fields
    cal_his = this_user["cal_his"]
    carb_his = this_user["carb_his"]
    fat_his = this_user["fat_his"]
    prot_his = this_user["prot_his"]

    for i in range(diff):
        cal_his.insert(0, 0)
        carb_his.insert(0, 0)
        fat_his.insert(0, 0)
        prot_his.insert(0, 0)

    # connect to database and update
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]

        who = {"netid": netid}
        update = {
            "$set": {
                "last_login" : today,
                "daily_rec" : [],
                "daily_serv" : [],
                "daily_nut" : [],
                "cal_his" : cal_his,
                "carb_his" : carb_his,
                "fat_his" : fat_his,
                "prot_his" : prot_his
            }
        }
        try:
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
# Note: right now, dict keys for nutrtion facts is labeled as "calories", "carbs", "fats", "proteins" and vals are doubles
def __calculatenutrition__(recipeids, servings):
    entry_cal = 0
    entry_carb = 0
    entry_fat = 0
    entry_prot = 0

    for recipeid, serving in zip(recipeids, servings):
        nut = find_one_nutrition(recipeid)
        if nut is None:
            print(f"Could not find recipe with recipid: {recipeid}")
            return
        entry_cal = entry_cal + nut["calories"]*serving
        entry_carb = entry_carb + nut["carbs"]*serving
        entry_fat = entry_fat + nut["fats"]*serving
        entry_prot = entry_prot + nut["proteins"]*serving
    return

# Update user's consumed good: add to daily plate
# Note: Entry is a dict of the following form {"entry_num" : INT, "recipeids" : [ARRAY OF RECIPE IDS], "servings" : [ARRAY OF SERVINGS] }
def addconsumed(netid, entry):
    this_user = finduser(netid)
    if this_user is None:
        return

    # calculated added cals and macronutrients
    entry_cal, entry_carb, entry_fat, entry_prot = __calculatenutrition__(entry["recipeids"], entry["servings"])

    # update
    daily_rec = this_user["daily_rec"]
    daily_serv = this_user["daily_serv"]
    daily_nut = this_user["daily_nut"]
    daily_rec.append(entry["recipeids"])
    daily_serv.append(entry["servings"])
    daily_nut.append({"calories" : entry_cal,
                    "carbs" : entry_carb,
                    "fats" : entry_fat,
                    "proteins": entry_prot})

    cal_his = this_user["cal_his"]
    carb_his = this_user["carb_his"]
    fat_his = this_user["fat_his"]
    prot_his = this_user["prot_his"]

    cal_his[0] = cal_his[0] + entry_cal
    carb_his[0] = carb_his[0] + entry_carb
    fat_his[0] = fat_his[0] + entry_fat
    prot_his[0] = prot_his[0] + entry_prot

    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        who = {"netid": netid}
        update = {
            "$set": {
                "daily_rec" : daily_rec,
                "daily_serv" : daily_nut,
                "daily_nut" : daily_nut,
                "cal_his" : cal_his,
                "carb_his" : carb_his,
                "fat_his" : fat_his,
                "prot_his" : prot_his
            }
        }
        try:
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
    return

# Update user's consumed good: edit foods from an entry from daily plate 
# This implementation can handle edits of foods, like adding a food or changing serving size, as well as deleting
def deleteconsumed(netid, entry):
    this_user = finduser(netid)
    if this_user is None:
        return

    # calculated added cals and macronutrients
    entry_cal, entry_carb, entry_fat, entry_prot = __calculatenutrition__(entry["recipeids"], entry["servings"])

    # update
    daily_rec = this_user["daily_rec"]
    daily_serv = this_user["daily_serv"]
    daily_rec[entry["entry_num"]] = entry["recipeids"]
    daily_serv.append[entry["entry_num"]] = entry["servings"]

    daily_nut = this_user["daily_nut"]
    old_nut = daily_nut[entry["entry_num"]] 
    cal_diff = old_nut["calories"] - entry_cal
    carb_diff = old_nut["carbs"] - entry_carb
    fat_diff = old_nut["fats"] - entry_fat
    prot_diff = old_nut["proteins"] - entry_prot
    daily_nut[entry["entry_num"]] = {"calories" : entry_cal,
                                    "carbs" : entry_carb,
                                    "fats" : entry_fat,
                                    "proteins": entry_prot}

    cal_his = this_user["cal_his"]
    carb_his = this_user["carb_his"]
    fat_his = this_user["fat_his"]
    prot_his = this_user["prot_his"]

    cal_his[0] = cal_his[0] - cal_diff
    carb_his[0] = carb_his[0] - carb_diff
    fat_his[0] = fat_his[0] - fat_diff
    prot_his[0] = prot_his[0] - prot_diff

    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        who = {"netid": netid}
        update = {
            "$set": {
                "daily_rec" : daily_rec,
                "daily_serv" : daily_nut,
                "daily_nut" : daily_nut,
                "cal_his" : cal_his,
                "carb_his" : carb_his,
                "fat_his" : fat_his,
                "prot_his" : prot_his
            }
        }
        try:
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
def deleteuser(netid):
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        who = {"netid": netid}
        try:
            result = users_collection.delete_one(who)
            print(f"# of deleted documents: {result.deleted_count}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
        return

# USED FOR TESTING FOR NOW 
def main(): 
    deleteuser("jm0278")
    newuser("Jewel", "jm0278", datetime(2004, 3, 9), 2000)
    userlogin("jm0278")
    return

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()