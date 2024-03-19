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

# Delete food entires prior to today and updates dining hall menus for the next two weeks 
def updatemenu(menu_list):
    with connectmongo() as client:
        db = client.db
        menu_col = db.menus

        eastern_time = pytz.timezone('US/Eastern')
        today = datetime.today(eastern_time)

        documents_to_delete = {"date": {"$lt": today}}

        try:
            delete_result = menu_col.delete_many(documents_to_delete)
            print(f"# of deleted documents: {delete_result.deleted_count}")
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
def querymenudisplay(date, mealtime, dhall = None):
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
            return result
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)
            
# Testing
def main():
    newmenu = {
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
        }
    updatemenu(newmenu)
    result1 = querymenudisplay("2024-03-02", "Lunch", "Rockefeller & Mathey Colleges")
    print(result1)
    result2 = querymenudisplay("2024-03-02", "Lunch", "NCW")
    print(result2)
    result3 = querymenudisplay("2024-03-02", "Lunch")
    print(result3)
    
    sys.exit(0)
    

if __name__ == '__main__':
    main()