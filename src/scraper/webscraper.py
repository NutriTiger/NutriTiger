#!/usr/bin/env python

# ----------------------------------------------------------------------
# webscraper.py
# Author: Eric
# ----------------------------------------------------------------------

import requests
import json
import sys
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------

# Pre-defined constants, may need developer maintanance if html format
# changes (unlikely)

# Base URL to retrive the html for the menu item
BASE_LABEL_URL = "https://menus.princeton.edu/dining/_Foodpro/online-menu/label.asp?RecNumAndPort="
CALORIES_INDEX = 1
CALORIES_OFFSET = 9
PROTEIN_OFFSET = 8
CARBS_OFFSET = 11
FATS_OFFSET = 10
CHOLESTEROL_OFFSET = 12
SODIUM_OFFSET = 7
SUGAR_OFFSET = 9
FIBER_OFFSET = 16
VITAMIND_OFFSET = 14
POTASSIUM_OFFSET = 11
CALCIUM_OFFSET = 9
IRON_OFFSET = 6
INGREDIENTS_CLASS = "labelingredientsvalue"
ALLERGENS_CLASS = "labelallergensvalue"

# ---------------------------------------------------------------------


def main():
    """
    The main function uses the other functions defined in this file to
    obtain a JSON object with nutrition information of a menu item in a preferred
    format and prints it to stdout.
    """

    # A sample recipeid to obtain nutrition information from
    SAMPLE_RECIPEID = 530602

    # Obtains the nutrition information
    nutrition_information = get_nutrition_from_recipe(SAMPLE_RECIPEID)
    
    # Prints the nutrition information nicely to stdout
    print(json.dumps(nutrition_information, indent=4, default=str))

# ---------------------------------------------------------------------


def get_nutrition_from_recipe(recipeid):
    """
    Based on the provided recipeid get_nutrition_from_recipe obtains
    the nutritional information from the html of the nutrition website
    and returns the created JSON object.
    """

    # Attempt to make the request to a create JSON object from the recipeid
    try:
        # Generate the URL to make the request
        COMBINED_URL = BASE_LABEL_URL + str(recipeid)

        # Make the request and save the content
        request = requests.get(COMBINED_URL)
        html_content = request.content

        # Parse the content and create the nutrition object to return
        soup = BeautifulSoup(html_content, "html.parser")
        nutrition_json = {}

        # Insert the recipeid
        nutrition_json["recipeid"] = recipeid
        # Insert the name of the item, which is the first h2 tag
        nutrition_json["mealname"] = soup.find("h2").text
        # Insert the calories, which is the second sequential element with id facts2
        nutrition_json["calories"] = soup.find_all(id="facts2")[CALORIES_INDEX].text[CALORIES_OFFSET:]

        # Obtains entries from the table that represents a nutrition label
        nutrition_table_details = soup.find_all(id="facts4")

        # For each element in the table, extract the number for each item
        for element in nutrition_table_details:
            # The title for what nutritional information a value represents is usaully a child element
            title = element.findChild()

            # Extract the quantity for each item in the nutrition table
            if title is not None:
                title = title.text.strip()
                if title == "Protein":
                    nutrition_json["protein"] = element.text[PROTEIN_OFFSET:]
                if title == "Tot. Carb.":
                    nutrition_json["carbs"] = element.text[CARBS_OFFSET:]
                if title == "Total Fat":
                    nutrition_json["fats"] = element.text[FATS_OFFSET:]
                if title == "Cholesterol":
                    nutrition_json["cholesterol"] = element.text[CHOLESTEROL_OFFSET:]
                if title == "Sodium":
                    nutrition_json["sodium"] = element.text[SODIUM_OFFSET:]

            # Extract the quantity for items with no seperate title element
            if element.text.strip().startswith("Sugars"):
                nutrition_json["sugar"] = element.text[SUGAR_OFFSET:]
            if element.text.strip().startswith("Dietary Fiber"):
                nutrition_json["fiber"] = element.text[FIBER_OFFSET:]

        # Obtains entries from the list in the nutrition label
        nutrition_table_list = soup.find_all("li")

        # For each entry in the list extract the value from the text
        for element in nutrition_table_list:
            element = element.text.strip()
            if element.startswith("Vitamin D"):
                nutrition_json["vitd"] = element.replace(" ", "")[VITAMIND_OFFSET:]
            if element.startswith("Potassium"):
                nutrition_json["potassium"] = element.replace(" ", "")[POTASSIUM_OFFSET:]
            if element.startswith("Calcium"):
                nutrition_json["calcium"] = element.replace(" ", "")[CALCIUM_OFFSET:]
            if element.startswith("Iron"):
                nutrition_json["iron"] = element.replace(" ", "")[IRON_OFFSET:]

        # Saves the ingredients and allergens list as a Python list to the JSON object
        nutrition_json["ingredients"] = soup.find("span", {"class": INGREDIENTS_CLASS}).text.split(", ")
        nutrition_json["allergen"] = soup.find("span", {"class": ALLERGENS_CLASS}).text.split(", ")

        return nutrition_json
    
    except Exception as ex:
        print(sys.argv[0] + ":", ex, file=sys.stderr)


if __name__ == "__main__":
    main()
