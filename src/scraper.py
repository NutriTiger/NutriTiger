import requests
import sys
from bs4 import BeautifulSoup

"""
Notes:

This file may not be needed anymore if MobileApp API calls work

Sources Used:
https://www.geeksforgeeks.org/python-web-scraping-tutorial/
https://towardsdatascience.com/xml-scraping-done-right-6ac66eef9efc

Location 05: CJL
Location 03: Forbes
Location 04: Grad
Location 01: Rocky + Maddy
Location 08: Whitman & Butler
Location 06: Yeh West

"""

def main():
    # Pre-defined constants, needs developer maintanance
    LOCATION_NUMS = ["01", "03", "04", "05", "06", "08"]
    LOCATION_DESCRIPTION = ["Rockefeller & Mathey Colleges", 
                            "Forbes College", "Graduate College", 
                            "Center for Jewish Life", 
                            "Yeh & New West Colleges", 
                            "Whitman & Butler Colleges"]
    
    # Complete JSON object to store the menus for one day
    data = {}

    # We can loop through all locations and obtain menu items as needed
    for location_num, location_description in zip(LOCATION_NUMS, LOCATION_DESCRIPTION):
        location_menu = get_daily_menu(location_num)
        data[location_description] = location_menu

    print(data)

# ---------------------------------------------------------------------


def get_daily_menu(location_num):
    # Will add a predefined location list and loop through each one to collect information
    base_menus_url = "https://menus.princeton.edu/dining/_Foodpro/online-menu/menu2.asp?"

    location_parameter = "locationNum=" + location_num
    combined_url = base_menus_url + location_parameter

    data = {}

    try:
        request = requests.get(combined_url)
        xml_content = request.content

        soup = BeautifulSoup(xml_content, "xml")
        mealsList = soup.find_all("meal")

        for meal in mealsList:
            mealType = meal.get_attribute_list("name")[0]
            data["meal"] = mealType
            entreeList = meal.find_all("entree")

            for entree in entreeList:
                entreeDescription = entree.get_attribute_list("type")[0][3:-3]
                data["entreeDescription"] = entreeDescription
                data["entreeName"] = entree.find("name").contents[0]
                data["recipeNumber"] = entree.find("recnum").contents[0]
                data["allergens"] = entree.find("allergens").contents[0]
        
        return data
    
    except Exception as ex:
        print(sys.argv[0] + ":", ex, file=sys.stderr)

if __name__ == "__main__":
    main()
