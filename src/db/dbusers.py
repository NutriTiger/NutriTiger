import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import ssl
import os
#----------------------------------------------------------------------
# Contributors:
# Jewel Merriman and Oyu Enkhbold
#
#----------------------------------------------------------------------

# Create new user profile: include calorie count, personal info
def newuser():
    return

# Update user's calorie goal
def updategoal():
    return

# INSIDE UPDATEDCONSUMED: organize macro/calorie count:
def __updatenutrition__():
    return

# Update user's consumed good: add to daily plate
def addconsumed():
    return

# Update user's consumed good: delete entry from daily plate
def deleteconsumed():
    return

# Retrive user's profile (including name/netid, goals, consumed)
def finduser():
    return

# delete user's data entries
def deleteuser():
    return

# to test connection
def main(): 

    # BEFORE YOU MUST export your mongodb username and password to environment 
    password = os.getenv("MONGODB_PASSWORD")
    username = os.getenv("MONGODB_USERNAME")

    uri = f"mongodb+srv://{username}:{password}@aws-m0-cluster.cywlmar.mongodb.net/?retryWrites=true&w=majority&appName=aws-m0-cluster"

    # Create a new client and connect to the server
    try: 
        client = MongoClient(uri)
    except Exception as e:
        print(e)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()