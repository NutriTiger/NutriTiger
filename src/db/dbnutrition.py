import pymongo
from dbfunctions import connectmongo
import sys
import datetime
import pytz
#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold and Jewel Merriman
#
#----------------------------------------------------------------------

# Create new food item -- should already include the net id field of user
def addpersonalfood(new_food):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        
        try:
            result = nutrition_col.insert_one(new_food)
            document_id = result.inserted_id
            print(f"_id of inserted document: {document_id}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Inserts nutrition information of the upcoming two weeks of food
def addmenunutrition(new_foods):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        
        try:
            result = nutrition_col.insert_many(new_foods)
            document_ids = result.inserted_ids
            print(f"_id of inserted documents: {document_ids}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
        

# Deletes all nutrition information of food items prior to this week
def deletenutritioninfo():
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        eastern_time = pytz.timezone('US/Eastern')
        eastern_time = pytz.timezone('US/Eastern')
        today = datetime.today(eastern_time)
        day_of_week = today.weekday()
        dt = today - datetime.timedelta(days = day_of_week)

        documents_to_delete = {"date": {"$lt": dt}}
        try:
            result = nutrition_col.delete_many(documents_to_delete)
            print(f"# of deleted documents: {result.deleted_count}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
        
# Retrieve nutritional information of singular food item
def find_one_nutrition(recipeid):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        document_to_find = {"recipeid": recipeid}
        try:
            result = nutrition_col.find_one(document_to_find)
            print(f"found document: {result}")
            return result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Retrieve nutritional information of multiple food items based on recipeids
def find_many_nutrition(recipeids):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        documents_to_find = {"recipeid": recipeids}
        try:
            result = nutrition_col.find(documents_to_find)
            print(f"found documents: {result}")
            return result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
