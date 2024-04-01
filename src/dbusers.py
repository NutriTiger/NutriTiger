import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, time
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

'''
Sets the user document with netid: netid to user_profile
Returns updated user profile
'''
def __setuser__(netid, user_profile):
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        who = {"netid": netid}
        try:
            updated = users_collection.find_one_and_update(who, {"$set": user_profile}, new=True)
            if updated is None:
                print(f"Database has changed while running. There does not exists a document with netid : {netid}")
            return updated
        except pymongo.errors.OperationFailure:
                print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
                sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
                print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
                sys.exit(1)

#-----------------------------------------------------------------------

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
    return {"calories" : entry_cal,
            "carbs" : entry_carb,
            "fats" : entry_fat,
            "proteins": entry_prot}

#-----------------------------------------------------------------------
'''
Updates the nutrient history for this_user, adding or subtracting the entry_nut
Factor must be -1 for subtracting, and +1 for adding
'''
def __updatehistory__(this_user, entry_nut, factor):
    cal_his = this_user["cal_his"]
    carb_his = this_user["carb_his"]
    fat_his = this_user["fat_his"]
    prot_his = this_user["prot_his"]

    cal_his[0] = cal_his[0] + entry_nut["calories"] * factor
    carb_his[0] = carb_his[0] + entry_nut["carbs"] * factor
    fat_his[0] = fat_his[0] + entry_nut["fats"] * factor
    prot_his[0] = prot_his[0] + entry_nut["proteins"] * factor

#-----------------------------------------------------------------------

'''
Create a new user document with netid: netid and caloricgoal: cal
Returns the new user's profile as a dict
'''
def newuser(netid, cal):
    # check that this user does not already exist
    this_user = finduser(netid)
    if this_user is not None:
        print(f"A user with netid {netid} already exists.")
        return this_user
    
    ########### FOR TESTING DATE
    #eastern_time = pytz.timezone('US/Eastern')
    #today_date = datetime(2024, 3, 14)
    #today = eastern_time.localize(today_date)

    # create new document for this user
    date_obj = datetime.now(pytz.timezone('US/Eastern')).date()
    today = datetime.combine(date_obj, time.min)
    user_document = {"_id": bson.ObjectId(), 
                    #"name" : name, 
                    "netid" : netid, 
                    #"bday" : bday, 
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

    # connect to database and add user
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        try:
            users_collection.insert_one(user_document)
            print(f"Created new user with netid: {netid}.")
            return user_document
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

#-----------------------------------------------------------------------
'''
If this is first contact of the day for user with netid: netid, updates fields
Returns updated user profile
'''
def userlogin(netid):
    this_user = finduser(netid)
    if this_user is None:
        return None

    # calculate difference between today and last entry
    date_obj = datetime.now(pytz.timezone('US/Eastern')).date()
    today = datetime.combine(date_obj, time.min)
    last_login = this_user["last_login"]
    diff = (today.date() - last_login.date()).days
 
    # if it's the same day, no updates necessary
    if (diff == 0):
        print("same day login")
        return this_user

    # update fields
    for i in range(diff):
        this_user["cal_his"].insert(0, 0)
        this_user["carb_his"].insert(0, 0)
        this_user["fat_his"].insert(0, 0)
        this_user["prot_his"].insert(0, 0)
    this_user["last_login"] = today
    this_user["daily_rec"] = []
    this_user["daily_serv"] = []
    this_user["daily_nut"] = []
    
    return __setuser__(netid, this_user)

#-----------------------------------------------------------------------

'''
Set the calorie goal to cal for user with netid: netid
Returns the updated profile for the user with netid: netid
'''
def updategoal(netid, cal):
    this_user = finduser(netid)
    if this_user is None:
        return
    this_user["caloricgoal"] = cal
    return __setuser__(netid, this_user)

#-----------------------------------------------------------------------

'''
Adds an entry to the daily plate of the user with netid:netid 
Returns the updated user profile
Note: Entry is a dict of the following form {"recipeids" : [ARRAY OF RECIPE IDS], "servings" : [ARRAY OF SERVINGS]}
'''
def addEntry(netid, entry):
    this_user = finduser(netid)
    if this_user is None:
        return None

    # calculated added cals and macronutrients
    entry_nut = __calculatenutrition__(entry["recipeids"], entry["servings"])

    # update
    this_user["daily_rec"].append(entry["recipeids"])
    this_user["daily_serv"].append(entry["servings"])
    this_user["daily_nut"].append(entry_nut)

    __updatehistory__(this_user, entry_nut, 1)
    return __setuser__(netid, this_user)

#-----------------------------------------------------------------------

'''
Deletes an entry with entry_num from the daily plate of the user with netid: netid 
Returns the updated user profile
Note: Entry num ranges from 0 to total number of entries - 1 for the user (0th indexed)
'''
def deleteEntry(netid, entry_num):
    this_user = finduser(netid)
    if this_user is None:
        return None

    # update
    entry_nut = this_user["daily_nut"][entry_num]
    this_user["daily_rec"].pop(entry_num)
    this_user["daily_serv"].pop(entry_num)
    this_user["daily_nut"].pop(entry_num)
    __updatehistory__(this_user, entry_nut, -1)
    
    return __setuser__(netid, this_user)

#-----------------------------------------------------------------------

'''
Deletes a food item with food_num from entry with entry_num from the daily plate of the user with netid: netid 
Returns the updated user profile
Note: Entry num ranges from 0 to total number of entries - 1 for the user (0th indexed)
Note: Food num is also 0th indexed
'''
def delFood(netid, entry_num, food_num):
    this_user = finduser(netid)
    if this_user is None:
        return None
    
    food_rec = this_user["daily_rec"][entry_num].pop(food_num)
    food_serv = this_user["daily_serv"][entry_num].pop(food_num)
    food_nut = __calculatenutrition__([food_rec], [food_serv])
    entry_nut = this_user["daily_nut"][entry_num]
    entry_nut["calories"] = entry_nut["calories"] - food_nut["calories"]
    entry_nut["carbs"] = entry_nut["carbs"] - food_nut["carbs"]
    entry_nut["fats"] = entry_nut["fats"] - food_nut["fats"]
    entry_nut["proteins"] = entry_nut["proteins"] - food_nut["proteins"]
    __updatehistory__(this_user, food_nut, -1)
    
    return __setuser__(netid, this_user)

#-----------------------------------------------------------------------

'''
Updates serving size to new_serv of a food item with food_num from entry with entry_num from the daily plate of the user with netid: netid 
Returns the updated user profile
Note: Entry num ranges from 0 to total number of entries - 1 for the user (0th indexed)
Note: Food num is also 0th indexed
Note: New serving size is a double
'''
def editFood(netid, entry_num, food_num, new_serv):
    this_user = finduser(netid)
    if this_user is None:
        return None
    
    # calculate difference
    food_serv = this_user["daily_serv"][entry_num][food_num]
    if (food_serv == new_serv):
        print("serving size is the same")
        return this_user
    food_rec = this_user["daily_rec"][entry_num][food_num]
    old = __calculatenutrition__([food_rec], [food_serv])
    serv_fact = new_serv/food_serv
    diff_nut = {"calories" : old["calories"]*serv_fact - old["calories"], 
                "carbs" : old["carbs"]*serv_fact - old["carbs"],
                "fats" : old["fats"]*serv_fact - old["fats"],
                "proteins" : old["proteins"]*serv_fact - old["proteins"]}
    
    # update user profile
    this_user["daily_serv"][entry_num][food_num] = new_serv
    entry_nut = this_user["daily_nut"][entry_num]
    entry_nut["calories"] = entry_nut["calories"] + diff_nut["calories"]
    entry_nut["carbs"] = entry_nut["carbs"] + diff_nut["carbs"]
    entry_nut["fats"] = entry_nut["fats"] + diff_nut["fats"]
    entry_nut["proteins"] = entry_nut["proteins"] + diff_nut["proteins"]
    __updatehistory__(this_user, diff_nut, 1)
    
    return __setuser__(netid, this_user)

#-----------------------------------------------------------------------

'''
Returns the profile of the user with netid: netid as a dict
'''
def finduser(netid):
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

#-----------------------------------------------------------------------

'''
Deletes the user profile with netid: netid. 
Returns the number of deleted documents, 0 if user with netid: netid was not found
Note: Should only return 1 or 0, as there should not be multiple users with the same netid
'''
def deleteuser(netid):
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        who = {"netid": netid}
        try:
            result = users_collection.delete_one(who)
            print(f"# of deleted documents: {result.deleted_count}")
            return result.deleted_count
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

#-----------------------------------------------------------------------

# USED FOR TESTING FOR NOW 
def main(): 
    entry = {"recipeids": [12345, 1], "servings": [2, 1.5]}
    # addEntry("jm0278", entry)
    addEntry("jm0278", entry)
    # print(deleteEntry("jm0278", 0))

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()