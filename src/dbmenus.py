import pymongo
from dbfunctions import connectmongo
import sys
from datetime import datetime, timedelta

#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold and Jewel Merriman
# Handle menus insertion by the scraper and handles dhall menu display
#----------------------------------------------------------------------

# Delete all menu documents and nutrition documents (except custom) 
# and inserts list of menu items (menu_list) to menu collection
def update_menu(menu_list):
    with connectmongo() as client:
        db = client.db
        menu_col = db.menus
        nutri_col = db.nutrition
        documents_to_delete = {}

        try:
            query_documents = menu_col.find(documents_to_delete)
            recipeid_to_delete = []

            # Deletes all nutrition documents that are not custom
            nutri_doc_to_delete = {"access": {"$exists": False}}
            delete_recipeid_result = nutri_col.delete_many(nutri_doc_to_delete)
            delete_result = menu_col.delete_many(documents_to_delete)
            # print(f"# of deleted documents: {delete_result.deleted_count}")
            if not menu_list:
                print("Menu list is empty, no menus added to the database", file = sys.stderr)
                return
            add_result = menu_col.insert_many(menu_list)
            document_ids = add_result.inserted_ids
            # print(f"# of documents inserted: {str(len(document_ids))}")
            # print(f"_id of inserted documents: {document_ids}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?", file = sys.stderr)
            return
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.", file = sys.stderr)
            return

# Retrive food items for menu by date (mealtime, and dhall are optional)
def query_menu_display(date, mealtime= None, dhall = None):
    with connectmongo() as client:
        db = client.db
        menu_col = db.menus

        # Strip the time portion to get the start of today in Eastern Time
        start_day = date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Define the end of today as just before midnight in Eastern Time
        end_day = start_day + timedelta(days=1) - timedelta(microseconds=1)

        if dhall and mealtime:
            documents_to_find = {"date": {
            "$gte": start_day,
            "$lt": end_day}, "mealtime": mealtime, "dhall": dhall}
        elif dhall:
            documents_to_find = {"date": {
            "$gte": start_day,
            "$lt": end_day}, "dhall": dhall}
        elif mealtime:
            documents_to_find = {"date": {
            "$gte": start_day,
            "$lt": end_day}, "mealtime": mealtime}
        else:
            documents_to_find = {"date": {
            "$gte": start_day,
            "$lt": end_day}}

        try: 
            result = menu_col.find(documents_to_find)
            #print(f"cursor: {result}")

            list_result = list(result)
            if not list_result:
                print("No menu documents found")
                return []
            return list_result
    
        except pymongo.errors.OperationFailure as e:
            print(e)
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?", file = sys.stderr)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(e)
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.", file = sys.stderr)
# TESTING
def main():
    date1 = datetime.fromisoformat('2020-01-06T00:00:00.000Z'[:-1] + '+00:00')
    date2 = datetime.fromisoformat('2020-01-06T00:00:00.000Z'[:-1] + '+00:00')
    date3 = datetime.fromisoformat('2020-01-06T00:00:00.000Z'[:-1] + '+00:00')

    newmenu = [
        {"date": date1,
        "dhall": "Rockefeller & Mathey Colleges",
        "mealtime": "Lunch",
        "data":{
            "grill": {"food1":1234,"food2":234},
            "area": {"food1":356,"food2":897}
        }
        },
        {
       "date": date2,
        "dhall": "Whitman & Butler Colleges",
        "mealtime": "breakfast",
        "data":{
            "fruit": {"food1":234,"food2":789},
            "area": {"food1":123,"food2":234}
        }
        }
        
    ]
    emptymenu = []
    update_menu(emptymenu)
    
    sys.exit(0)
    

if __name__ == '__main__':
    main()