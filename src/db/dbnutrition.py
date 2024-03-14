import pymongo
from dbfunctions import connectmongo
import sys
#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold and Jewel Merriman
#
#----------------------------------------------------------------------

# Create new food item -- should have the net id field of user
def addpersonalfood(new_food):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        
        try:
            result = nutrition_col.insert_one(new_food)
            document_id = result.inserted_id
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
        print(f"_id of inserted document: {document_id}")
    return

# Inserts nutrition information of the upcoming two weeks of food
def addmenunutrition(new_foods):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        
        try:
            result = nutrition_col.insert_many(new_foods)
            document_ids = result.inserted_ids
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
        print(f"_id of inserted documents: {document_ids}")
    return

# Deletes all nutrition information of food items prior to today's date
def deletenutritioninfo():
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        today
        documents_to_delete = {"date": {"$lt": }}
        try:
            result = nutrition_col.insert_many(documents_to_delete)
            document_ids = result.inserted_ids
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
        print(f"_id of inserted documents: {document_ids}")
    return