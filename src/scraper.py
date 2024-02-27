import requests
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
    # Will add a predefined location list and loop through each one to collect information
    base_menus_url = "https://menus.princeton.edu/dining/_Foodpro/online-menu/menu2.asp?"
    # Pre-defined constant, needs developer maintanance
    location_nums = ["01", "03", "04", "05", "06", "08"]
    
    # We can loop through all locations and obtain menu items as needed
    for location_num in location_nums:
        location_parameter = "locationNum=" + location_num

        combined_url = base_menus_url + location_parameter
        request = requests.get(combined_url)
        if request.status_code != 200:
            raise Exception("Error retrieving URL")
        
        print(request.content)
        xml_content = request.content

        soup = BeautifulSoup(xml_content, "xml")
        print(soup.find("name"))

if __name__ == "__main__":
    main()
