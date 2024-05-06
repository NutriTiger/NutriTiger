import pymongo
from dbfunctions import connectmongo
import sys
from datetime import datetime
import pytz
import sys

#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold and Jewel Merriman
# Handles nutrition information insertion in nutrition collection
# Note: recipeID logic = [netID]-[maxID] where maxID is a nunber
#       of custom food items created by the user
#----------------------------------------------------------------------

# Retrieves the maximum ID for a user (from the "users" collection) to create a custom food recipeID.
def get_maxid(netid):
    try:
        with connectmongo() as client:
            db = client.db
            users_collection = db["users"]
            # Will only return the max_id
            this_user = users_collection.find_one({"netid": netid}, {"_id": 0, "max_id": 1})
            if this_user is None:
                print(f"No document found with netid: {netid}", file=sys.stderr)
                return None
            return this_user.get('max_id', None)
    except pymongo.errors.OperationFailure:
        print("Authentication error: check if your DB user is authorized for write operations.")
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Server timeout: ensure your IP address is in the Access List on Atlas.")

# Increments the max_id field of a user after adding a document.
def update_maxid(netid):
    with connectmongo() as client:
        db = client.db
        users_collection = db["users"]
        who = {"netid": netid}
        try:
            result = users_collection.update_one(who, {"$inc": {"max_id": 1}})
            if result.matched_count == 0:
                print(f"No document found with netid: {netid}", file=sys.stderr)
                return
            elif result.modified_count == 0:
                print(f"Document with netid: {netid} was not updated.", file=sys.stderr)
                return
            return
        except pymongo.errors.OperationFailure as e:
            print(f"An authentication error occurred: {e}", file=sys.stderr)
            return
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(f"The server timed out: {e}", file=sys.stderr)
            return

# Retrieves the current max_id for a user and then increments it.
def find_and_update_maxid(netid):
    try:
        with connectmongo() as client:
            db = client.db
            users_collection = db["users"]
            who = {"netid": netid}

            # Will only return the max_id
            this_user = users_collection.find_one(who, {"_id": 0, "max_id": 1})
            if this_user is None:
                print(f"No document found with netid: {netid}", file=sys.stderr)
                return None
            
            result = users_collection.update_one(who, {"$inc": {"max_id": 1}})

            if result.modified_count == 0:
                print(f"Document with netid: {netid} was not updated.", file=sys.stderr)

            return this_user.get('max_id', None)
    except pymongo.errors.OperationFailure:
        print("Authentication error: check if your DB user is authorized for write operations.", file=sys.stderr)
        return
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Server timeout: ensure your IP address is in the Access List on Atlas.", file=sys.stderr)
        return

# Inserts nutritional information for an array of new food items into the nutrition collection.
# Accepts new_foods as a list of BSON objects.
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
                    print(f"Non-dict item found: {item} of type {type(item)}", file=sys.stderr)
                    
            add_result = nutrition_col.insert_many(new_foods)
            document_ids = add_result.inserted_ids
            print(f"_id of inserted documents: {document_ids}", file=sys.stderr)
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?", file=sys.stderr)
            return
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.",file=sys.stderr)
            return
        

# Retrieves nutritional information for a single food item based on the given recipe ID.
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
            return
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            return


# Deletes a custom food item from the nutrition collection based on the specified recipe ID.
# Returns True if successful, False otherwise.
def del_custom_food(recipeid):
    with connectmongo() as client:
        print(recipeid)
        db = client.db
        nutrition_col = db.nutrition
        try:
            document_to_delete = {'recipeid': recipeid}

            # [FUTURE USE]
            # document = nutrition_col.find_one(document_to_delete)
            # if 'public_id' in document:
            #     public_id = document['public_id']
            #     response = photos.delete_one_photo(public_id)
            #     if response.get('result') == 'ok':
            #         print(f"Successfully deleted {response.get('public_id')}")
            #     else:
            #         print(f"Failed to delete {response.get('public_id')}. Reason: {response.get('result')}")
            #         return False
            nutrition_col.delete_one(document_to_delete)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        
# Deletes multiple custom food items from the nutrition collection based on the specified array of recipe IDs.
# Returns True if successful, False otherwise.
def del_many_custom_food(recipeids):
    print("in del_many_custom_food")
    print(recipeids)

    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition
        try:
            # Create a query to match any of the recipe IDs in the list
            query = {'recipeid': {'$in': recipeids}}

            # [FUTURE USE]
            # documents = nutrition_col.find(query)
            # public_ids = [doc['public_id'] for doc in documents if 'public_id' in doc] 

            # # Deletes photos if they exist, otherwise continue w nutrition deletion
            # if len(public_ids) > 0:
            #     success = photos.delete_many_photos(public_ids)
            #     if not success:
            #         return False

            result = nutrition_col.delete_many(query)
            print(f"Deleted {result.deleted_count} documents.")

            # Check if the number of deleted documents matches the number of IDs provided
            if result.deleted_count == len(recipeids):
                return True
            else:
                print(f"Expected to delete {len(recipeids)}, but deleted {result.deleted_count}.")
                return False
        except Exception as e:
            print("Exception within del_many_custom")
            print(f"Error during deletion: {e}")
            return False

# Creates a new custom food item in the nutrition collection. The recipe ID is generated using the user's net ID and max ID.
def add_custom_food(name, netid, nutrition):
    # Gets max_id and increment
    num_current = find_and_update_maxid(netid)

    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        recipeid = netid + '-'+ str(num_current + 1)
        today = datetime.now(pytz.timezone('US/Eastern'))

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
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Retrieves nutritional information for multiple food items based on a list of recipe IDs.
# Returns a list of BSON objects with nutritional information, or an empty list if no matching documents are found.
def find_many_nutrition(recipeids):
    if not recipeids:
        print("Empty recipeid list")
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


# Retrieves all custom nutrition information for a user, sorted by the most recently created documents.
def find_all_custom_nutrition(netid):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        documents_to_find = {"access": netid}# Define the sort order - descending by 'created_at' field
        try:
            # Execute find operation with sorting
            result = list(nutrition_col.find(documents_to_find).sort("date", pymongo.DESCENDING))
            print(f"found documents: {result}")
            if len(result) == 0:
                print("No custom nutrition documents found")
                return
            return result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?", file = sys.stderr)
            return
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.", file = sys.stderr)
            return

# Retrieves a specific custom nutrition document for a user based on the net ID and lowercase name (identifier).
def find_one_custom_nutrition(netid, lowercase_name):
    with connectmongo() as client:
        db = client.db
        nutrition_col = db.nutrition

        documents_to_find = {"access": netid, "check": lowercase_name}
        try:
            result = nutrition_col.find_one(documents_to_find)
            print(f"found documents: {result}")
            if not result:
                print("No custom nutrition document found")
                return
            return result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?", file = sys.stderr)
            return
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.", file = sys.stderr)
            return 

#-----------------------------------------------------------------------

# ONLY USE TO DELETE CUSTOM FOOD ITEMS
# Main function that deletes all custom food items for a specific user.
def main(): 
    
    with connectmongo() as client:
        db = client.db
        col = db.nutrition

        # Write your netID here
        netid = ''
        documents_to_delete = {"access": netid}

        del_result = col.delete_many(documents_to_delete)
        print(del_result)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()