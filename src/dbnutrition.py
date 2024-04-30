import pymongo
from dbfunctions import connectmongo
from dbusers import get_maxid, update_maxid
import sys
from datetime import datetime, time
import pytz
from PIL import Image
import io
from bson.binary import Binary
import photos
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

            for item in new_foods:
                if not isinstance(item, dict):
                    print(f"Non-dict item found: {item} of type {type(item)}")
                    
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


# Deletes personal food item
# Recipeid has netid and unique number
# Returns true if successful, false is unsuccessful
def del_personal_food(recipeid):
    with connectmongo() as client:
        print(recipeid)
        db = client.db
        nutrition_col = db.nutrition
        try:
            document_to_delete = {'recipeid': recipeid}

            # Deletes image first
            document = nutrition_col.find_one(document_to_delete)
            if 'public_id' in document:
                public_id = document['public_id']
                response = photos.delete_one_photo(public_id)
                if response.get('result') == 'ok':
                    print(f"Successfully deleted {response.get('public_id')}")
                else:
                    print(f"Failed to delete {response.get('public_id')}. Reason: {response.get('result')}")
                    return False
            nutrition_col.delete_one(document_to_delete)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
# Deletes personal food items
# Recipeids is in array of recipeids
# Returns true if successful, false is unsuccessful
def del_many_personal_food(recipeids):
    print("in del_many_personal_food")
    print(recipeids)

    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        try:
            # Create a query to match any of the recipe IDs in the list
            query = {'recipeid': {'$in': recipeids}}

            # Deletes images first
            documents = nutrition_col.find(query)
            public_ids = [doc['public_id'] for doc in documents if 'public_id' in doc] 

            # Deletes photos if they exist, otherwise continue w nutrition deletion
            if len(public_ids) > 0:
                success = photos.delete_many_photos(public_ids)
                if not success:
                    return False

            result = nutrition_col.delete_many(query)
            print(f"Deleted {result.deleted_count} documents.")

            # Check if the number of deleted documents matches the number of IDs provided
            if result.deleted_count == len(recipeids):
                return True
            else:
                print(f"Expected to delete {len(recipeids)}, but deleted {result.deleted_count}.")
                return False
        except Exception as e:
            print("Exception within del_many_personal")
            print(f"Error during deletion: {e}")
            return False

# Create new food item -- should already include the net id field of user
# Nutrition is dictionary
def add_personal_food(name, netid, nutrition):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        try:
            num_current = get_maxid(netid)
            print(num_current)
            recipeid = netid + '-'+ str(num_current + 1)
            print(recipeid)

            date_obj = datetime.now(pytz.timezone('US/Eastern')).date()
            today = datetime.combine(date_obj, time.min)

            try:
                document_to_add = {"mealname" : name, 
                    "access": netid,
                    "recipeid" : recipeid,
                    "date": today,
                    **nutrition
                    }
                result = nutrition_col.insert_one(document_to_add)
                document_id = result.inserted_id
                print(f"_id of inserted document: {document_id}")
                update_maxid(netid)
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
def find_many_nutrition(recipeids):
    if not recipeids:
        print("empty recipeid list")
        return []

    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        try:
            # Construct the pipeline for aggregation
            pipeline = [
                {"$match": {"recipeid": {"$in": recipeids}}},
                {"$addFields": {"__order": {"$indexOfArray": [recipeids, "$recipeid"]}}},
                {"$sort": {"__order": 1}},
                {"$project": {
                    "_id": 0,
                    "recipeid": 1,
                    "mealname": 1,
                    "link": 1,
                    "calories": 1,
                    "servingsize": 1,
                    "proteins": 1,
                    "carbs": 1,
                    "fats": 1,
                    "ingredients": 1,
                    "allergen": 1
                }}
            ]
            
            result_list = list(nutrition_col.aggregate(pipeline))

            # Create a dictionary with recipeids as keys for quick lookup
            result_dict = {result["recipeid"]: result for result in result_list}

            # Fill in missing documents with empty dictionaries
            result_list = [result_dict.get(recipeid, {}) for recipeid in recipeids]

            return result_list

        except Exception as e:
            print(f"Error: {e}")
            return []


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
def find_one_personal_nutrition(netid, lowercase_name):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        documents_to_find = {"access": netid, "check": lowercase_name}
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

    # update_nutrition(nutrition)
    # data = find_one_nutrition('560154')
    # print(data['calories'])
    # list = [12345, 54321]
    # result = find_many_nutrition(list)
    # print(result[0]['calories'])
    # link = "https://www.cs.princeton.edu/courses/archive/spr24/cos333/index.html"
    # add_personal_food("ANOTHER", "oe7583", personal, link)
    # list = find_all_personal_nutrition("oe7583")
    # for item in list:
    #     print(item)
    # find_one_personal_nutrition("oe7583", 1)

    # date_obj = datetime.now(timezone('US/Eastern')).date()
        # today = datetime.combine(date_obj, time.min)
    
    with connectmongo() as client:
        db = client.db
        col = db.personal_nutrition
        documents_to_delete = {"access": "oe7583"}

        del_result = col.delete_many(documents_to_delete)
        print(del_result)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()