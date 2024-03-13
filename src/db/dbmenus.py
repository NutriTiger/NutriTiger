import pymongo
from dbfunctions import connectmongo
import sys
import datetime
#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold and Jewel Merriman
#
#----------------------------------------------------------------------

# INSIDE UPDATE MENU: delete outdated food entries
def __deletemenu__():

    return

# Update dining hall menus for the next two weeks --> accepts list as paramter
def updatemenu(menu_list):
    db = connectmongo()
    menu_col = db.menus

    try:
        result = menu_col.insert_many(menu_list)
        document_ids = result.inserted_ids
    except pymongo.errors.OperationFailure:
        print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
        sys.exit(1)
    except pymongo.errors.ServerSelectionTimeoutError:
        print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
        sys.exit(1)
    print(f"# of documents inserted: {str(len(document_ids))}")
    print(f"_id of inserted document: {document_ids}")

    return

# Retrive food items for the next week (dhall display page)
def querymenu(dhall):
    db = connectmongo()

    # Determine week

    # query items

    return

# Retrieve food that a specific user has consumed during the day
def querytoday(user_id):
    db = connectmongo()
    return