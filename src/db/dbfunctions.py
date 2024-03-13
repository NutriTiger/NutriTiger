import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import os
import sys
#----------------------------------------------------------------------
# Contributors:
# Jewel Merriman and Oyu Enkhbold
#
# Based off of atlas starter packet: 
# https://github.com/mongodb-university/atlas_starter_python/blob/master/atlas-starter.py
#----------------------------------------------------------------------

# Connect to NutriTiger MongoDB database and return database object
def connectmongo():
    password = os.getenv("MONGODB_PASSWORD")
    username = os.getenv("MONGODB_USERNAME")

    uri = f"mongodb+srv://{username}:{password}@aws-m0-cluster.cywlmar.mongodb.net/?retryWrites=true&w=majority&appName=aws-m0-cluster"
    try:
        client = pymongo.MongoClient(uri)
  
    # return a friendly error if a URI error is thrown 
    except pymongo.errors.ConfigurationError:
        print("An Invalid URI host error was received. Make sure your connection string is valid. See README for more details.")
        sys.exit(1)

    # return database named "NT-db"
    return client[NT-db]
