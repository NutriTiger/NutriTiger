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

# INSIDE UPDATE MENU: delete food entries prior to the start of this week (Monday)
def __deletemenu__():
    with connectmongo() as client:
        db = client.db
        menus_col = db.menus
        eastern_time = pytz.timezone('US/Eastern')
        today = datetime.today(eastern_time)
        day_of_week = today.weekday()
        dt = today - datetime.timedelta(days = day_of_week)

        documents_to_delete = {"date": {"$lt": dt}}
        try:
            result = menus_col.delete_many(documents_to_delete)
            print(f"# of deleted documents: {result.deleted_count}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)


# Update dining hall menus for the next two weeks --> accepts list as paramter
def updatemenu(menu_list):
    __deletemenu__()

    with connectmongo() as client:
        db = client.db
        menu_col = db.menus
        try:
            result = menu_col.insert_many(menu_list)
            document_ids = result.inserted_ids
            print(f"# of documents inserted: {str(len(document_ids))}")
            print(f"_id of inserted document: {document_ids}")
            return
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("The server timed out. Is your IP address added to Access List? To fix this, add your IP address in the Network Access panel in Atlas.")
            sys.exit(1)


# Retrive food items for the next week (dhall display page)
def querymenudisplay(dhall):
    with connectmongo() as client:
        db = client.db
        menu_col = db.menus

        # determine start and end of the week
        eastern_time = pytz.timezone('US/Eastern')
        today = datetime.today(eastern_time)
        day_of_week = today.weekday()
        start_of_week = today - datetime.timedelta(days = (day_of_week - 1))
        end_of_week = today + datetime.timedelta(days = (7 - day_of_week))
        
        documents_to_find = {"date": {"$gt": start_of_week, "$lt": end_of_week},
                             "dhall": {"$eq": dhall}}
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


# Retrive food items for today's menu at dhall
def querymenutoday(dhall):
    with connectmongo() as client:
        db = client.db
        menu_col = db.menus

        # determine start and end of the week
        eastern_time = pytz.timezone('US/Eastern')
        today = datetime.today(eastern_time)
        
        documents_to_find = {"date": {"$eq": today},
                             "dhall": {"$eq": dhall}}
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
