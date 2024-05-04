import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, time
import pytz
from dbfunctions import connectmongo
import dbnutrition
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

    nut = dbnutrition.find_many_nutrition(recipeids)
    for index, dictionary in enumerate(nut):
        if dictionary:
            entry_cal += dictionary["calories"] * servings[index]
            entry_carb += dictionary["carbs"] * servings[index]
            entry_fat += dictionary["fats"] * servings[index]
            entry_prot += dictionary["proteins"] * servings[index]
    
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

    # create new document for this user
    date_obj = datetime.now(pytz.timezone('US/Eastern')).date()
    today = datetime.combine(date_obj, time.min)
    user_document = {"_id": bson.ObjectId(), 
                    "netid" : netid,  
                    "caloricgoal" : cal,
                    "join_date" : today,
                    "last_login" : today,
                    "cal_his" : [0],
                    "carb_his" : [0],
                    "fat_his" : [0],
                    "prot_his" : [0],
                    "daily_rec" : [],
                    "daily_serv" : [],
                    "daily_nut" : [],
                    "max_id": 0
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
Returns the max_id for a user.
'''
def get_maxid(netid):
    this_user = finduser(netid)
    return this_user["max_id"]
#-----------------------------------------------------------------------
'''
Updates the max_id for a user.
'''
def update_maxid(netid):
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        who = {"netid": netid}
        try:
            result = users_collection.update_one(who, {"$inc": {"max_id": 1}})
            if result.matched_count == 0:
                print(f"No document found with netid: {netid}")
            elif result.modified_count == 0:
                print(f"Document with netid: {netid} was not updated.")
        except pymongo.errors.OperationFailure as e:
            print(f"An authentication error occurred: {e}")
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(f"The server timed out: {e}")
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
    entry_nut = entry["nutrition"]

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
Deletes each entry within the array of entry numbers from the daily plate of this_user 
Returns the updated user profile
Note: Entry num ranges from 0 to total number of entries - 1 for the user (0th indexed)
'''
def deleteManyEntry(this_user, array_of_entry_nums):
    sorted_entry_nums = sorted(array_of_entry_nums, reverse = True)

    totalNut = {"calories": 0, 
                "carbs": 0, 
                "fats": 0, 
                "proteins": 0}
    # update
    for entry_num in sorted_entry_nums:
        entry_nut = this_user["daily_nut"][entry_num]
        totalNut["calories"] += entry_nut["calories"]
        totalNut["carbs"] += entry_nut["carbs"]
        totalNut["fats"] += entry_nut["fats"]
        totalNut["proteins"] += entry_nut["proteins"]

        this_user["daily_rec"].pop(entry_num)
        this_user["daily_serv"].pop(entry_num)
        this_user["daily_nut"].pop(entry_num)
    __updatehistory__(this_user, totalNut, -1)
    
    return this_user

#-----------------------------------------------------------------------

'''
Deletes a food item with food_num from entry with entry_num from the daily plate of this_user
Returns the updated user profile
Note: Entry num ranges from 0 to total number of entries - 1 for the user (0th indexed)
Note: Food num is also 0th indexed
'''
def delFood(this_user, entry_num, food_num):
    
    food_rec = this_user["daily_rec"][entry_num].pop(food_num)
    food_serv = this_user["daily_serv"][entry_num].pop(food_num)
    food_nut = __calculatenutrition__([food_rec], [food_serv])
    entry_nut = this_user["daily_nut"][entry_num]
    entry_nut["calories"] = entry_nut["calories"] - food_nut["calories"]
    entry_nut["carbs"] = entry_nut["carbs"] - food_nut["carbs"]
    entry_nut["fats"] = entry_nut["fats"] - food_nut["fats"]
    entry_nut["proteins"] = entry_nut["proteins"] - food_nut["proteins"]
    __updatehistory__(this_user, food_nut, -1)
    
    return this_user

#-----------------------------------------------------------------------

'''
Updates serving size to new_serv of a food item with food_num from entry with entry_num from the daily plate of this_user 
Returns the updated user profile
Note: Entry num ranges from 0 to total number of entries - 1 for the user (0th indexed)
Note: Food num is also 0th indexed
Note: New serving size is a double
'''
def editFood(this_user, entry_num, food_num, new_serv):
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

    return this_user

#-----------------------------------------------------------------------
'''
One function for all edit plate possibilities. Takes 3 arguments:
    netid
    entriesToDelete: an array of entry numbers (0 indexed) to be deleted
    foodsToDelete: an array of dictionaries [{index: entrynum, foods:[foodnums]}]
    servingsToEdit: a dictionary {entrynum-foodnum: new_serving}
'''

def editPlateAll(netid, entriesToDelete, foodsToDelete, servingsToEdit):
    this_user = finduser(netid)
    if this_user is None:
        return None
    
    # edit all of the servings first
    for key, value in servingsToEdit.items():
        entrynum, foodnum = key.split('-')
        editFood(this_user, int(entrynum), int(foodnum), value)
    
    # delete foods
    for dictionary in foodsToDelete:
        foods = sorted(dictionary["foods"], reverse=True)
        for foodnum in foods:
            delFood(this_user, dictionary["index"], foodnum)
    
    # delete entries
    deleteManyEntry(this_user, entriesToDelete)

    # update profile
    for index, entry in enumerate(this_user["daily_rec"]):
        if len(entry)==0:
            this_user["daily_rec"].pop(index)
            this_user["daily_serv"].pop(index)
            this_user["daily_nut"].pop(index)
    return __setuser__(netid, this_user)
    

#-----------------------------------------------------------------------
'''
Handles deleting the recipes in deletedFoods array, deleting them from
user profile

'''
def handleDeleteCustomNutrition(netid, deletedFood):
    this_user = finduser(netid)
    daily_recids = this_user["daily_rec"]
    for entrynum, recids in enumerate(daily_recids):
        for foodnum, recid in enumerate(recids):
            foods_to_del = []
            if recid == deletedFood:
                foods_to_del.append(foodnum)
        foods_to_del = sorted(foods_to_del, reverse=True)
        for food in foods_to_del:
            delFood(this_user, entrynum, food)

    for index, entry in enumerate(this_user["daily_rec"]):
        if len(entry)==0:
            this_user["daily_rec"].pop(index)
            this_user["daily_serv"].pop(index)
            this_user["daily_nut"].pop(index)
    return __setuser__(netid, this_user)

def handleManyDeleteCustomNutrition(netid, deletedFoods):
    this_user = finduser(netid)
    daily_recids = this_user["daily_rec"]
    for entrynum, recids in enumerate(daily_recids):
        for foodnum, recid in enumerate(recids):
            foods_to_del = []
            if recid in deletedFoods:
                foods_to_del.append(foodnum)
        foods_to_del = sorted(foods_to_del, reverse=True)
        for food in foods_to_del:
            delFood(this_user, entrynum, food)

    for index, entry in enumerate(this_user["daily_rec"]):
        if len(entry)==0:
            this_user["daily_rec"].pop(index)
            this_user["daily_serv"].pop(index)
            this_user["daily_nut"].pop(index)
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
Returns the calorie goal of a user based on netid
'''
def findsettings(netid):
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        try:
            pipeline = [
                {"$match": {"netid": netid}},
                {"$project": {"_id": 0, "caloricgoal": 1, "join_date": 1, "last_login": 1}}
            ]
            result = list(users_collection.aggregate(pipeline))
            if not result:
                print(f"There does not exist a document with netid: {netid}")
                return None
            return result[0]  # Return the first (and only) result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)


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
    editFood("jm0278", 0, 0, 100)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()