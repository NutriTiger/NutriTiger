# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')

from flask import Flask, render_template
from CASClient import CASClient

app = Flask(__name__)
_cas = CASClient()


@app.route('/')
def hello_world():
    #print("HERE!")
    #netid = _cas.authenticate()
    #print(netid)
    #netid = netid.rstrip()
    # test data
    LOCATION_DESCRIPTION = ["Rockefeller & Mathey Colleges",
                        "Forbes College", "Graduate College",
                        "Center for Jewish Life",
                        "Yeh & New West Colleges",
                        "Whitman & Butler Colleges"]
    all_foods = ["Teriyaki Chicken", "General Tso's Tofu"]
    nutritional_content = "Serving Size: 8 oz\nCalories: 200\nProtein: 10 g\nFat: 10 g\nCarbs: 20 g\n\nIngredients: Chicken, Soy Sauce, Sugar, Sesame Seeds, Canola Oil, Salt, Pepper, Chili\n\nAllergens: Wheat, soy, tree nuts"

    location_food_dict = {location: all_foods for location in LOCATION_DESCRIPTION}

    todays_date = 'Monday, March 11th'

    return render_template('dhallmenus.html', todays_date=todays_date, location_food_dict=location_food_dict, nutritional_content=nutritional_content)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
