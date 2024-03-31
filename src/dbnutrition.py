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
# call update_menu before to delete nutrition info
# new_foods is list of bson objects
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
# Recipeid is int
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

            if not result:
                print("No documents found")
                return
            return result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Create new food item -- should already include the net id field of user
# Link is string, nutrition is dictionary
def add_personal_food(name, netid, nutrition, link):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        items_to_find = {"access": netid}

        try:
            find_prev_personal = nutrition_col.find(items_to_find)
            prev_personal = list(find_prev_personal)
            num_current = len(prev_personal)
            print(num_current)
            recipeid = (num_current + 1)
            try:
                document_to_add = {"mealname" : name, 
                    "access": netid,
                    "recipeid" : recipeid,
                    "link": link,
                    **nutrition
                    }
                result = nutrition_col.insert_one(document_to_add)
                document_id = result.inserted_id
                print(f"_id of inserted document: {document_id}")
                return
            except:
                print("Issue with insert for personal doc")
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Retrieve nutritional information of multiple food items based on recipeids
# Return list of bson objects with nutrition information (entries are None if recipeid does not exist)
def find_many_nutrition(recipeids, personal=False):
    if not recipeids:
        print("empty recipeid list")
        return
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        try:
            # all recipeids and isn't personal
            result_list = []
            for id in recipeids:
                doc_to_find = {"recipeid": id, "access": { "$exists": personal }}
                try:
                    result = nutrition_col.find_one(doc_to_find)
                except:
                    print("Error with finding obj")
                    return
                print(f"found document: {result}")
                result_list.append(result)
            return result_list
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
            if not result:
                print("No personal nutrition document found")
                return
            return result
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
        },
        {"recipeid": 24821,
         "mealname": "Tomato Soup",
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
    personal = {"calories": 100,
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

    update_nutrition(nutrition)
    data = find_one_nutrition('560154')
    print(data['calories'])
    list = [12345, 54321]
    result = find_many_nutrition(list)
    print(result[0]['calories'])
    link = "https://www.cs.princeton.edu/courses/archive/spr24/cos333/index.html"
    add_personal_food("ANOTHER", "oe7583", personal, link)
    # list = find_all_personal_nutrition("oe7583")
    # for item in list:
    #     print(item)
    # find_one_personal_nutrition("oe7583", 1)


#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()