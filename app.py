# ----------------------------------------------------------------------
# 
# app.py
#
# ----------------------------------------------------------------------

# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')

from flask import Flask, render_template, request, redirect
import time
from CASClient import CASClient

#--------------------------------------------------------------------

app = Flask(__name__)
_cas = CASClient()

#--------------------------------------------------------------------

# Code used from PennyFlaskJinja/penny.py from Lecture 10
def get_ampm():
    current_hr = int(time.strftime('%I'))
    am_pm = time.strftime('%p')
    if am_pm == "AM":
        return 'morning'
    elif am_pm == "PM" and current_hr < 6:
        return 'afternoon'
    return 'evening'

#--------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    # Check if it is a user's first visit
    visited_before = request.cookies.get('visited_before')
    if 'visited_before' is None:
        # indicate first contact
        visited_before = '(None)'
        # Redirect to set initial goals page
        return redirect('/welcome')
    return redirect('/homepage')

#--------------------------------------------------------------------

@app.route('/homepage', methods=['GET'])
def homepage():
    #netid = _cas.authenticate()
    #netid = netid.rstrip()
    netid = 'ab1234' # Placeholder netID
    return render_template('homepage.html', ampm=get_ampm(), netid=netid)

#--------------------------------------------------------------------

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

#--------------------------------------------------------------------

@app.route('/dhallmenus', methods=['GET'])
def dhall_menus():
    # Fetch menu data from database
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

#--------------------------------------------------------------------

@app.route('/welcome', methods=['GET', 'POST'])
def first_contact():
    if request.method == 'POST':

        # Get value entered into the calorie goal box
        user_goal = request.form['line']

        # Validate value: with bootstrap and js, limit values that user can enter
        # (ex. no negative values, no characters, no special characters)
        # Store value into database

    return render_template('firstcontact.html')

#--------------------------------------------------------------------

@app.route('/history', methods=['GET'])
def history():

    return render_template('history.html')

#--------------------------------------------------------------------

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Update database with new input value
        new_user_goal = request.form['line']

        # Validate value
        # Store value into database

    return render_template('settings.html')

#--------------------------------------------------------------------

@app.route('/editingplate', methods=['POST'])
def editing_plate():
    return render_template('editingplate.html')

#--------------------------------------------------------------------

@app.route('/logfood', methods=['POST'])
def log_food():
    return render_template('logfood.html')

#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
