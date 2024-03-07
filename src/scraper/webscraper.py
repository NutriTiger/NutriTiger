import requests
from bs4 import BeautifulSoup

"""
Notes:

Location 05: CJL
Location 03: Forbes
Location 04: Grad
Location 01: Rocky + Maddy
Location 08: Whitman & Butler
Location 06: Yeh West

"""

def main():
    # When we XML scrape we can get data for each recipe
    base_label_url = "https://menus.princeton.edu/dining/_Foodpro/online-menu/label.asp?RecNumAndPort=530602"

    request = requests.get(base_label_url)
    if request.status_code != 200:
        raise Exception("Error retrieving URL")
    
    #print(request.content)
    html_content = request.content

    soup = BeautifulSoup(html_content, "html")
    # Print all the contents
    print(soup.contents)
    # Print all the div elements, will need to refine to search for nutritional facts
    print(soup.find_all("div"))

if __name__ == "__main__":
    main()
