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

# Delete food entries and nutrition info prior to today and updates dining hall 
# menus for the next two weeks 
def update_menu(menu_list):
    with connectmongo() as client:
        db = client.db
        menu_col = db.menus
        nutri_col = db.nutrition

        date_obj = datetime.now(timezone('US/Eastern')).date()
        today = date_obj.strftime("%Y-%m-%d")

        documents_to_delete = {"date": {"$lt": today}}
        try:
            query_documents = menu_col.find(documents_to_delete)
            recipeid_to_delete = []
            for item in query_documents:
                for id in item["recipenums"]:
                    recipeid_to_delete.append(id)
    
            print(recipeid_to_delete)
            if len(recipeid_to_delete) == 0:
                print("no recipeids to delete")
                return
            nutri_doc_to_delete = {"recipeid": {"$eq": recipeid_to_delete}}
            if len(recipeid_to_delete) == 1:
                delete_recipeid_result = nutri_col.delete_one(nutri_doc_to_delete)
            else:
                delete_recipeid_result = nutri_col.delete_many(nutri_doc_to_delete)

            delete_result = menu_col.delete_many(documents_to_delete)
            print(f"# of deleted documents: {delete_result.deleted_count}")
            if not menu_list:
                print("Menu list is empty, no menus added to the database")
                return
            add_result = menu_col.insert_many(menu_list)
            document_ids = add_result.inserted_ids
            print(f"# of documents inserted: {str(len(document_ids))}")
            print(f"_id of inserted documents: {document_ids}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)

# Retrive food items for menu by date, mealtime, and dhall (optional)
def query_menu_display(date, mealtime, dhall = None):
    with connectmongo() as client:
        db = client.db
        menu_col = db.menus

        if dhall is None:
            documents_to_find = {"date": {"$eq": date}, "mealtime": {"$eq": mealtime}}
        else:
            documents_to_find = {"date": {"$eq": date}, "mealtime": {"$eq": mealtime}, "dhall":{"$eq": dhall}}

        try:
            result = menu_col.find(documents_to_find)
            print(f"found documents: {result}")
            list_result = list(result)
            if len(list_result) == 0:
                print("No menu documents found")
                return
            return list_result
    
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
            
# Testing
def main():
    newmenu = [
        {"date": "2024-03-02",
        "dhall": "Rockefeller & Mathey Colleges",
        "mealtime": "Lunch",
        "type": "Soup of the Day",
        "fooditems": [
            "Roma House Beef Vegetable Soup",
            "Vegan White Bean & Escarole Soup"
        ],
        "recipenums": [
            "459978",
            "020207"
        ]
        },
        {
        "date": "2024-03-02",
        "dhall": "Rockefeller & Mathey Colleges",
        "mealtime": "Lunch",
        "type": "Breakfast Bars",
        "fooditems": [
            "Bagels",
            "French Toast Sticks",
            "Oatmeal Bar",
            "Omelet Bar with Pork Options",
            "Pancake & Waffle Toppings"
        ],
        "recipenums": [
            "217001",
            "280007",
            "270052",
            "061001",
            "280002"
        ]
        },
        {
        "date": "2024-03-02",
        "dhall": "Rockefeller & Mathey Colleges",
        "mealtime": "Lunch",
        "type": "Main Entree",
        "fooditems": [
            "Seared Salmon with Lemon Herb Butter"
        ],
        "recipenums": [
            "510308"
        ]
        },
        {
        "date": "2024-03-02",
        "dhall": "NCW",
        "mealtime": "Lunch",
        "type": "Main Entree",
        "fooditems": [
            "Seared Salmon with Lemon Herb Butter"
        ],
        "recipenums": [
            "510308"
        ]
        }
    ]
    emptymenu = []
    updatemenu(newmenu)
    # result1 = querymenudisplay("2024-03-02", "Lunch", "Rockefeller & Mathey Colleges")
    # print("querymenudisplay: 3/2, lunch, roma")
    # for row in result1:
    #     print(row)
    # result2 = querymenudisplay("2024-03-02", "Lunch", "NCW")
    # print("querymenudisplay: 3/2, lunch, NCW")
    # for row in result2:
    #     print(row)
    # result3 = querymenudisplay("2024-03-02", "Lunch")
    # print("querymenudisplay: 3/2, lunch")
    # for row in result3:
    #     print(row)
    
    sys.exit(0)
    

if __name__ == '__main__':
    main()