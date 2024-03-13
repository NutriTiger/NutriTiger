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

    soup = BeautifulSoup(html_content, "html.parser")
    # Print all the contents
    print(soup.contents)
    # Print all the div elements, will need to refine to search for nutritional facts
    #print(soup.find_all("div"))

    nutrition_json = {}
    nutrition_json["recipeid"] = 530602
    nutrition_json["mealname"] = soup.find("h2").text
    nutrition_json["calories"] = soup.find_all(id="facts2")[1].text[9:]

    nutrition_table_details = soup.find_all(id="facts4")
    for element in nutrition_table_details:
        title = element.findChild()
        if title is not None:
            if title.text.strip() == "Protein":
                print(title.text)
                nutrition_json["protein"] = element.text[8:]
            if title.text.strip() == "Tot. Carb.":
                print(title.text)
                nutrition_json["carbs"] = element.text[11:]
            if title.text.strip() == "Total Fat":
                print(title.text)
                nutrition_json["fats"] = element.text[10:]
            if title.text.strip() == "Cholesterol":
                print(title.text)
                nutrition_json["cholesterol"] = element.text[12:]
            if title.text.strip() == "Sodium":
                print(title.text)
                nutrition_json["sodium"] = element.text[7:]
        if element.text.strip().startswith("Sugars"):
            nutrition_json["sugar"] = element.text[9:]
        if element.text.strip().startswith("Dietary Fiber"):
            nutrition_json["fiber"] = element.text[16:]
        print(element.text)

    nutrition_table_list = soup.find_all("li")
    for element in nutrition_table_list:
        element = element.text.strip()
        if element.startswith("Vitamin D"):
            nutrition_json["vitd"] = element.replace(" ", "")[14:]
        if element.startswith("Potassium"):
            nutrition_json["potassium"] = element.replace(" ", "")[11:]
        if element.startswith("Calcium"):
            nutrition_json["calcium"] = element.replace(" ", "")[9:]
        if element.startswith("Iron"):
            nutrition_json["iron"] = element.replace(" ", "")[6:]

    nutrition_json["ingredients"] = soup.find("span", {'class': 'labelingredientsvalue'}).text.split(",")
    nutrition_json["allergen"] = soup.find("span", {'class': 'labelallergensvalue'}).text.split(",")

    print(nutrition_json)

if __name__ == "__main__":
    main()
