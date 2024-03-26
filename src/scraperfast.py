#!/usr/bin/env python

# ----------------------------------------------------------------------
# scraper.py
# Author: Eric
# ----------------------------------------------------------------------

"""
Notes:

Using manual scraper over MobileApp API to obtain entree descriptions

Sources Used:
https://www.geeksforgeeks.org/python-web-scraping-tutorial/
https://towardsdatascience.com/xml-scraping-done-right-6ac66eef9efc
https://realpython.com/python-concurrency/

Location 05: CJL
Location 03: Forbes
Location 04: Grad
Location 01: Rocky + Maddy
Location 08: Whitman & Butler
Location 06: Yeh West
"""

import sys
import datetime
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import webscraperfast

# ---------------------------------------------------------------------

# Pre-defined constants, needs developer maintanance

# Base URL to retrive the XML for the menus
BASE_MENUS_URL = "https://menus.princeton.edu/dining/_Foodpro/online-menu/menu2.asp?"
# Predefined location numbers and descriptions from campus dining
LOCATION_NUMS = ["01", "03", "04", "05", "06", "08"]
LOCATION_DESCRIPTION = ["Center for Jewish Life",
                        "Forbes College", "Rockefeller & Mathey Colleges",
                        "Whitman & Butler Colleges",
                        "Yeh & New West Colleges",
                        "Graduate College"]

# ---------------------------------------------------------------------


def main():
    """
    The main function uses the other functions defined in this file to
    obtain a list of JSON objects of today's menu items (or a specified range) 
    in a preferred format and print it to stdout.
    """

    todays_menu_items, todays_nutrition_list = asyncio.run(get_daily_menus())

    #for object in todays_menu_items:
    #    print(json.dumps(object, indent=4, default=str))
    
    #for object in todays_nutrition_list:
    #    print(json.dumps(object, indent=4, default=str))

    start_date = datetime.datetime(2024, 3, 26).date()
    end_date = datetime.datetime(2024, 3, 27).date()

    menu_items_list_range, menu_items_nutrition_list_range = asyncio.run(get_daily_menus_from_range(start_date, end_date))
    #print(menu_items_list_range)
    #print(menu_items_nutrition_list_range)

# ---------------------------------------------------------------------


async def get_daily_menus_from_range(start_date, end_date):
    """
    Given a start date and an end date, a list of lists of menu items
    and nutrition information corresponding to each day is returned. If
    both of the dates are the same or represent an invalid range an
    exception is thrown.
    """

    date_difference = (end_date - start_date).days

    if date_difference <= 0:
        raise Exception(sys.argv[0] + ":", "Invalid date range!")
    else:
        current_date = start_date
        menu_items_list = []
        menu_nutrition_list = []

        results = []

        while (current_date != (end_date + datetime.timedelta(days = 1))):
            print("Getting daily menus for", current_date)

            job = asyncio.ensure_future(get_daily_menus(current_date))
            results.append(job)
            
            current_date = current_date + datetime.timedelta(days = 1)

            """
            current_menu_items_list, current_menu_nutrition_list = get_daily_menus(current_date)
            menu_items_list.append(current_menu_items_list)
            menu_nutrition_list.append(current_menu_nutrition_list)

            current_date = current_date + datetime.timedelta(days = 1)
            """
        
        await asyncio.gather(*results, return_exceptions=True)
        
        for result in results:
            if result.result() is None:
                menu_items = []
                nutrition_items = []
            else:
                menu_items, nutrition_items = result.result()
            for obj1, obj2 in zip(menu_items, nutrition_items):
                menu_items_list.append(obj1)
                menu_nutrition_list.append(obj2)

        return menu_items_list, menu_nutrition_list

# ---------------------------------------------------------------------


async def get_daily_menus(date=""):
    """
    Based on the predefined location numbers in LOCATION_NUMS and
    descriptions in LOCATION_DESCRIPTION get_daily_menus obtains the
    menu for the specified date from every location into a list of JSON 
    objects. The objects are created based on the entree types. If no
    date is specified today's menus are returned.
    """

    # Complete list of JSON objects to store the menus for one day
    complete_menu_data_list = []
    complete_nutrition_data_list = []
    #temp = []
    distinct_recipeid_list = []

    # Obtain the menu items from each location
    async with aiohttp.ClientSession() as session:
        menu_results = []
        for location_num, location_description in zip(LOCATION_NUMS, LOCATION_DESCRIPTION):
            job = asyncio.ensure_future(get_daily_menu(location_num, location_description, distinct_recipeid_list, session, date))
            menu_results.append(job)
        await asyncio.gather(*menu_results, return_exceptions=True)

        # Can cause error if no data
        for result in menu_results:
            if result.result() is None:
                menu_list = []
                nutrition_list = []
            else:
                menu_list, nutrition_list = result.result()
            for obj1, obj2 in zip(menu_list, nutrition_list):
                complete_menu_data_list.append(obj1)
                complete_nutrition_data_list.append(obj2)

        #for test in temp:
        #    complete_nutrition_data_list.append(test)

    return complete_menu_data_list, complete_nutrition_data_list

# ---------------------------------------------------------------------


async def get_daily_menu(location_num, location_description, distinct_recipeid_list, session, date=""):
    """
    For a specific location, we make a request for the XML with the
    menu details and create JSON objects based on the unique entree
    types for each meal based on the provided location_num and
    location_description. The list of menu items for that location is
    returned for the specified date. If no date is specified today's
    menu is returned.
    """

    # Generate the URL to make the request
    LOCATION_PARAMETER = "locationNum=" + location_num
    DATE_PARAMETER = ""
    if date != "":
        DATE_PARAMETER = "&myaction=read&dtdate=" + return_formatted_date(date)
    COMBINED_URL = BASE_MENUS_URL + LOCATION_PARAMETER + DATE_PARAMETER

    print("Obtaining daily menu for", location_description)

    # Attempt to make the request to create JSON objects from the menu
    try:
        # Make the request and save the content
        async with session.get(COMBINED_URL) as request:
            xml_content = await request.text()
            soup = BeautifulSoup(xml_content, "xml")
            mealsList = soup.find_all("meal")

            # Final list will all JSON objects to return
            complete_menu_data_list = []
            complete_nutrition_data_list = []
            nutrition_results = []

            # Create JSON objects based on entree type for each meal
            for meal in mealsList:
                # Obtain the list of entries for that meal
                mealType = meal.get_attribute_list("name")[0]
                entreeList = meal.find_all("entree")
                
                # Stores the JSON objects for that entree type
                data = {}
                # Stores the JSON object for meals in each mealtype
                items_obj = {}
                # Stores the JSON object for mealtypes for a mealtime
                mealitems_obj = {}
                # Stores the previous entree description to combine
                # identical entree types for a meal
                oldEntreeDescription = ""

                # Go through each entree and add to the JSON object or
                # start a new one
                for i, entree in enumerate(entreeList):
                    # Get the description of the entree
                    entreeDescription = entree.get_attribute_list("type")[0][3:-3]

                    # If its not the first iteration and we are on a new
                    # entree description, start a new JSON object
                    if i > 0:
                        if entreeDescription != oldEntreeDescription:
                            # Save the data before clearing
                            mealitems_obj[oldEntreeDescription] = items_obj
                            
                            # Clear the data
                            items_obj = {}
                    
                    # If we are on a new data object, add the needed fields
                    if len(data) == 0:
                        if date != "":
                            data["date"] = date
                        else:
                            data["date"] = datetime.datetime.today()
                        data["dhall"] = location_description
                        data["mealtime"] = mealType

                    # Update the old entree and append the items to the JSON
                    oldEntreeDescription = entreeDescription
                    foodname = entree.find("name").text
                    recipeid = entree.find("recnum").text
                    items_obj[foodname] = recipeid

                    # Add the nutrition information for the recipe number to the list
                    if recipeid not in distinct_recipeid_list:
                        distinct_recipeid_list.append(recipeid)
                        job = asyncio.ensure_future(webscraperfast.get_nutrition_from_recipe(recipeid, session))
                        nutrition_results.append(job)
            
                mealitems_obj[oldEntreeDescription] = items_obj
                data["data"] = mealitems_obj
                complete_menu_data_list.append(data)

            await asyncio.gather(*nutrition_results, return_exceptions=True)
            
            for i, result in enumerate(nutrition_results):
                complete_nutrition_data_list.append(result.result())

            return complete_menu_data_list, complete_nutrition_data_list

    except Exception as ex:
        print(sys.argv[0] + ":", ex, file=sys.stderr)

# ---------------------------------------------------------------------


def return_formatted_date(date):
    """
    Given a datetime object, the object is parsed into a format that is
    returned as a parameter for the menu url to accept.
    """
    month_portion = str(date.month) + "%2F"
    day_portion = str(date.day) + "%2F"
    year_portion = str(date.year)

    return month_portion + day_portion + year_portion

if __name__ == "__main__":
    main()
