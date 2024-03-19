import pymongo
from dbfunctions import connectmongo
import sys
from datetime import datetime
from pytz import timezone
#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold and Jewel Merriman
#
#----------------------------------------------------------------------

# Inserts nutrition information of the upcoming two weeks of food (as input)
def update_nutrition(new_foods):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        
        try:
            if len(new_foods) == 0:
                print("new foods arr is empty")
                return

            add_result = nutrition_col.insert_many(new_foods)
            document_ids = add_result.inserted_ids
            print(f"_id of inserted documents: {document_ids}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
        

# Retrieve nutritional information of singular food item
def find_one_nutrition(recipeid):
    if not recipeid:
        print("no recipe id inputted")
        return
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        document_to_find = {"recipeid": recipeid}
        try:
            result = nutrition_col.find_one(document_to_find)
            print(f"found document: {result}")
            list_result = list(result)
            if len(list_result) == 0:
                print("No documents found")
                return
            return list_result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Create new food item -- should already include the net id field of user
def addpersonalfood(name, netid, nutrition):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        current_items = {"netid": netid}

        try:
            check = nutrition_col.find(current_items)
            document_ids = check.inserted_ids
            num_current = str(len(document_ids))
            recipeid = num_current + 1
            try:
                new_food = {"mealname" : name, 
                    "netid": netid,
                    "recipeid" : recipeid,
                    "calories" : nutrition[0], 
                    "proteins" : nutrition[1], 
                    "carbs" : nutrition[2],
                    "fats" : nutrition[3],
                    "chloesterol" : nutrition[4],
                    "sodium" : nutrition[5],
                    "calcium" : nutrition[6],
                    "vitd" : nutrition[7],
                    "potassium" : nutrition[8],
                    "iron" : nutrition[9],
                    "sugar" : nutrition[10],
                    "fiber" : nutrition[11],
                    "allergen": nutrition[12],
                    "ingredients": nutrition[13]
                    }
                result = nutrition_col.insert_one(new_food)
                document_id = result.inserted_id
                print(f"_id of inserted document: {document_id}")
                return
            except:
                print("issue with insert")
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Retrieve nutritional information of multiple food items based on recipeids
def find_many_nutrition(recipeids):
    if not recipeids:
        print("empty recipeid list")
        return
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        # all recipeids and isn't personal
        documents_to_find = {"recipeid": recipeids, "access": { "$exists": False }}
        try:
            result = nutrition_col.find(documents_to_find)
            print(f"found documents: {result}")
            list_result = list(result)
            if len(list_result) == 0:
                print("No nutrition documents found")
                return
            return list_result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Retrieve nutritional information of a user
def find_all_personal_nutrition(netid):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        documents_to_find = {"access": netid}
        try:
            result = nutrition_col.find(documents_to_find)
            print(f"found documents: {result}")
            list_result = list(result)
            if len(list_result) == 0:
                print("No personal nutrition documents found")
                return
            return list_result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Find one personal nutrition info with user's netid and recipeid
def find_one_personal_nutrition(netid, recipeid):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        documents_to_find = {"access": netid, "recipeid": recipeid}
        try:
            result = nutrition_col.find_one(documents_to_find)
            print(f"found documents: {result}")
            list_result = list(result)
            if len(list_result) == 0:
                print("No personal nutrition document found")
                return
            return list_result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)            

#-----------------------------------------------------------------------

# USED FOR TESTING FOR NOW 
def main(): 
    nutrition = [
        {"recipeid": 12345,
         "mealname": "Test Soup",
         "link": "https://www.cs.princeton.edu/courses/archive/spr24/cos333/index.html",
         "calories": 100,
         "proteins": 10,
         "carbs": 9,
         "fats": 8,
         "cholesterol": 7,
         "sodium": 6,
         "calcium": 5,
         "vitd": 4,
         "potassium": 3,
         "iron": 2,
         "sugar": 1,
         "fiber": 0,
         "allergen": "soy",
         "ingredients": "Flour, soy, water",
        }
    ]
    personal = [
        {"recipeid": 1,
         "mealname": "Test Salad",
         "link": "https://www.cs.princeton.edu/courses/archive/spr24/cos333/index.html",
         "calories": 100,
         "proteins": 10,
         "carbs": 9,
         "fats": 8,
         "cholesterol": 7,
         "sodium": 6,
         "calcium": 5,
         "vitd": 4,
         "potassium": 3,
         "iron": 2,
         "sugar": 1,
         "fiber": 0,
         "allergen": "soy",
         "ingredients": "Flour, soy, water",
         "access": "oe7583"
        }
    ]
    update_nutrition(nutrition)
    find_one_nutrition(12345)
    list = [12345, 22222]
    find_many_nutrition(list)
    addpersonalfood(personal)
    find_all_personal_nutrition("oe7583")
    find_one_personal_nutrition("oe7583", 1)


#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()