# ----------------------------------------------------------------------
# 
# app.py
#
# ----------------------------------------------------------------------

# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')
path.append('src/db')

from flask import Flask, render_template, request, redirect, make_response
import time
#from CASClient import CASClient
from src import dbusers
from src import dbmenus


#--------------------------------------------------------------------

app = Flask(__name__)
#_cas = CASClient()

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

    if visited_before is None:
        # Indicate first contact
        visited_before = None
        # Set cookie to mark user as visited now
        response = make_response(redirect('/welcome'))
        response.set_cookie('visited_before', 'True')
        return response
    
    return redirect('/homepage')

#--------------------------------------------------------------------

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    #netid = _cas.authenticate()
    #netid = netid.rstrip()

    # Placeholder values
    netid = 'jm0278' 
    curr_caltotal = 1500
    cursor = dbusers.finduser(netid)
    cal_goal = int(cursor['caloricgoal'])
    print(cal_goal)

    if request.method == 'POST':
        return redirect('/editingplate')
    
    ENTRIES = ["Entry 1", "Entry 2", "Entry 3"]
    all_foods = ["Teriyaki Chicken", "General Tso's Tofu"]

    entries_food_dict = {entry: all_foods for entry in ENTRIES}

    return render_template('homepage.html', ampm=get_ampm(), netid=netid,
                           curr_caltotal=curr_caltotal, cal_goal=cal_goal,
                           entries_food_dict=entries_food_dict)

#--------------------------------------------------------------------

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

#--------------------------------------------------------------------

@app.route('/dhallmenus', methods=['GET'])
def dhall_menus():
    # Fetch menu data from database
    # test data
    #data = dbmenus.querymenudisplay("2024-03-02", "Lunch")
    #print(data)
    not_weekend = True
    LOCATION_DESCRIPTION = ["Rockefeller & Mathey Colleges",
                        "Forbes College", "Graduate College",
                        "Center for Jewish Life",
                        "Yeh & New West Colleges",
                        "Whitman & Butler Colleges"]
    all_foods = ["Teriyaki Chicken", "General Tso's Tofu"]
    nutritional_content = "Serving Size: 8 oz\nCalories: 200\nProtein: 10 g\nFat: 10 g\nCarbs: 20 g\n\nIngredients: Chicken, Soy Sauce, Sugar, Sesame Seeds, Canola Oil, Salt, Pepper, Chili\n\nAllergens: Wheat, soy, tree nuts"

    location_food_dict = {location: all_foods for location in LOCATION_DESCRIPTION}
    time_of_day = 'Lunch'
    todays_date = 'Monday, March 11th'

    return render_template('dhallmenus.html', todays_date=todays_date, 
                           location_food_dict=location_food_dict, 
                           nutritional_content=nutritional_content, not_weekend=not_weekend, time_of_day=time_of_day)


#--------------------------------------------------------------------

@app.route('/welcome', methods=['GET', 'POST'])
def first_contact():
    if request.method == 'POST':
        # Placeholder netID
        netid = 'jm0278'
        # Get value entered into the calorie goal box
        user_goal = request.form['line']
        # Store value into database
        dbusers.updategoal(netid, user_goal)
        return redirect('/homepage')

    return render_template('firstcontact.html')

#--------------------------------------------------------------------

@app.route('/history', methods=['GET'])
def history():

    # Placeholder values
    avg_cals = 2000
    avg_pro = 50
    avg_carbs = 100
    avg_fat = 40

    return render_template('history.html', avg_cals=avg_cals, 
                           avg_pro=avg_pro, avg_carbs=avg_carbs, 
                           avg_fat=avg_fat)

#--------------------------------------------------------------------

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        netid = 'jm0278'
        new_user_goal = request.form['line']
        dbusers.updategoal(netid, new_user_goal)
        return redirect('/homepage')

    return render_template('settings.html')

#--------------------------------------------------------------------

@app.route('/editingplate', methods=['GET', 'POST'])
def editing_plate():

    # Placeholder values
    netid = 'jm0278' 
    curr_caltotal = 1500
    cursor = dbusers.finduser(netid)
    cal_goal = int(cursor['caloricgoal'])
    print(cal_goal)

    if request.method == 'POST':
        '''
        if request.form['action'] == 'close':
            # Close button action

        elif 'save_plate' in request.form:
            # Save button action
    
            return redirect('/homepage')
            '''
        return redirect('/homepage')
    
    ENTRIES = ["Entry 1", "Entry 2", "Entry 3"]
    all_foods = ["Teriyaki Chicken", "General Tso's Tofu"]

    entries_food_dict = {entry: all_foods for entry in ENTRIES}

    return render_template('editingplate.html', ampm=get_ampm(), netid=netid,
                           curr_caltotal=curr_caltotal, cal_goal=cal_goal,
                           entries_food_dict=entries_food_dict)

#--------------------------------------------------------------------

@app.route('/logfood', methods=['GET', 'POST'])
def log_food():
    if request.method == 'POST':
        return redirect('/homepage')
    return render_template('logfood.html')

#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
