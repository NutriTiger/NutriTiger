import pymongo
from dbfunctions import connectmongo
import sys
#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold and Jewel Merriman
#
#----------------------------------------------------------------------

# Create new food item
def newfood(new_food):
    db = connectmongo()
    nutrition_col = db.nutrition
    result = nutrition_col.insert_one(new_food)
    document_id = result.inserted_id
    try:
        nutrition_col.insert_one(new_food)
    except pymongo.errors.OperationFailure:
        print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
        sys.exit(1)
    except pymongo.errors.ServerSelectionTimeoutError:
        print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
        sys.exit(1)
    print(f"_id of inserted document: {document_id}")
    return

# Create new food item - specific to user (this is specific to entry)
# def newpersonalfood(new_food):


# INSIDE UPDATE MENU: delete outdated food entries
def __deletemenu__():
    return

# Update dining hall menus for the next two weeks --> put inside db
def updatemenu():
    return

# Retrive food items for the next week (dhall display page)
def querymenu():
    return

# Retrieve food that a specific user has consumed during the day
def querytoday():
    return