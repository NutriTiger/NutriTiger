# ----------------------------------------------------------------------
# 
# app.py
#
# ----------------------------------------------------------------------

# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')
path.append('src/db')

from flask import Flask, render_template, request, redirect, make_response, jsonify
import time
import datetime
import os
import dotenv
from pytz import timezone
#from CASClient import CASClient
from src import dbusers
from src import dbmenus
from src import utils
from src import auth


#--------------------------------------------------------------------

app = Flask(__name__)
dotenv.load_dotenv()
app.secret_key = os.environ['APP_SECRET_KEY']

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
    netid = auth.authenticate()
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
    netid = auth.authenticate()
    #netid = _cas.authenticate()
    #netid = netid.rstrip()

    # Placeholder values
    #netid = 'jm0278' 

    # will need to call whenever an existing user logs in
    profile = dbusers.userlogin(netid)

    curr_caltotal = profile['cal_his'][0]

    cal_goal = int(profile['caloricgoal'])

    # Copy pasted from editing plate method below
    cursor = dbusers.finduser(netid)
    entries_info = cursor['daily_rec']

    # Testing filling the entries
    ENTRIES = ["Entry " + str(i + 1) for i in range(len(entries_info))]
    foods_lists = [entry[:] for entry in entries_info]

    entries_food_dict = {}
    for i in range(len(ENTRIES)):
        entry = ENTRIES[i]
        foods = foods_lists[i]
        entries_food_dict[entry] = foods

    # When Edit Plate button is pressed
    if request.method == 'POST':
        return redirect('/editingplate')

    return render_template('homepage.html', ampm=get_ampm(), netid=netid,
                           curr_caltotal=curr_caltotal, cal_goal=cal_goal,
                           entries_food_dict=entries_food_dict)

#--------------------------------------------------------------------

@app.route('/about', methods=['GET'])
def about():
    netid = auth.authenticate()
    return render_template('about.html')

#--------------------------------------------------------------------

@app.route('/menus', methods=['GET'])
def dhall_menus():
    netid = auth.authenticate()
    # Fetch menu data from database
    # test data
    current_date = datetime.datetime.today()
    current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
    mealtime = utils.time_of_day(current_date.date(), current_date.time())
    is_weekend_var = utils.is_weekend(current_date.date())
    print('we made it here')

    data = dbmenus.query_menu_display(current_date_zeros, mealtime)
    print('past the data line')
    print(data)


    locations = ["Center for Jewish Life",
                        "Forbes College", "Rockefeller & Mathey Colleges",
                        "Whitman & Butler Colleges",
                        "Yeh & New West Colleges",
                        "Graduate College"]

    nutritional_content = "Serving Size: 8 oz\nCalories: 200\nProtein: 10 g\nFat: 10 g\nCarbs: 20 g\n\nIngredients: Chicken, Soy Sauce, Sugar, Sesame Seeds, Canola Oil, Salt, Pepper, Chili\n\nAllergens: Wheat, soy, tree nuts"

    todays_date = utils.custom_strftime(current_date)
    print(todays_date)

    return render_template('dhallmenus.html', todays_date=todays_date, locations=locations, data=data,
                           nutritional_content=nutritional_content, is_weekend_var=is_weekend_var, mealtime=mealtime)

@app.route('/update-menus-mealtime', methods=['GET'])
def update_menus_mealtime():
    netid = auth.authenticate()
    mealtime = request.args.get('mealtime')

    current_date = datetime.datetime.today()
    current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
    is_weekend_var = utils.is_weekend(current_date.date())

    data = dbmenus.query_menu_display(current_date_zeros, mealtime)
    print(data)


    locations = ["Center for Jewish Life",
                        "Forbes College", "Rockefeller & Mathey Colleges",
                        "Whitman & Butler Colleges",
                        "Yeh & New West Colleges",
                        "Graduate College"]

    nutritional_content = "Serving Size: 8 oz\nCalories: 200\nProtein: 10 g\nFat: 10 g\nCarbs: 20 g\n\nIngredients: Chicken, Soy Sauce, Sugar, Sesame Seeds, Canola Oil, Salt, Pepper, Chili\n\nAllergens: Wheat, soy, tree nuts"

    todays_date = utils.custom_strftime(current_date)
    print(todays_date)

    return render_template('dhallmenus_update.html', todays_date=todays_date, locations=locations, data=data,
                        nutritional_content=nutritional_content, is_weekend_var=is_weekend_var, mealtime=mealtime)

#--------------------------------------------------------------------

@app.route('/welcome', methods=['GET', 'POST'])
def first_contact():
    netid = auth.authenticate()
    if request.method == 'POST':
        # Placeholder netID
        #netid = 'jm0278'
        # Get value entered into the calorie goal box
        user_goal = request.form['line']
        # Store value into database
        if dbusers.finduser(netid) is None:
            dbusers.newuser(netid, user_goal)
        else:
            dbusers.updategoal(netid, user_goal)
        return redirect('/homepage')

    return render_template('firstcontact.html')

#--------------------------------------------------------------------

@app.route('/history', methods=['GET'])
def history():
    netid = auth.authenticate()
    # find current user
    profile = dbusers.finduser(netid)
    cal_his, carb_his, prot_his, fat_his, dates = utils.get_corresponding_arrays(profile['cal_his'], 
                                                                                profile['carb_his'],
                                                                                profile['prot_his'],
                                                                                profile['fat_his']
                                                                                )
    # calculate averages with user's specified range (7 days)
    his_range = 7
    avg_cals = utils.get_average(cal_his, his_range)
    avg_carbs = utils.get_average(carb_his, his_range)
    avg_pro = utils.get_average(prot_his, his_range)
    avg_fat = utils.get_average(fat_his, his_range)
    dates.reverse()
    cal_his.reverse()

    return render_template('history.html', 
                            avg_cals=round(avg_cals, 2), 
                            avg_pro=round(avg_pro, 2), 
                            avg_carbs=round(avg_carbs, 2), 
                            avg_fat=round(avg_fat,2),
                            dates = dates,
                            cals = cal_his,
                            prots = prot_his,
                            carbs = carb_his,
                            fats = fat_his
                            )

#--------------------------------------------------------------------

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    netid = auth.authenticate()
    if request.method == 'POST':
        #netid = 'jm0278'
        new_user_goal = request.form['line']
        dbusers.updategoal(netid, new_user_goal)
        return redirect('/homepage')

    return render_template('settings.html')

#--------------------------------------------------------------------

@app.route('/editingplate', methods=['GET', 'POST'])
def editing_plate():
    netid = auth.authenticate()

    # Placeholder values
    #netid = 'jm0278' 
    cursor = dbusers.finduser(netid)
    cal_goal = int(cursor['caloricgoal'])
    curr_caltotal = cursor['cal_his'][0]
    entries_info = cursor['daily_rec']

    # Testing filling the entries
    ENTRIES = ["Entry " + str(i + 1) for i in range(len(entries_info))]
    foods_lists = [entry[:] for entry in entries_info]

    entries_food_dict = {}
    for i in range(len(ENTRIES)):
        entry = ENTRIES[i]
        foods = foods_lists[i]
        entries_food_dict[entry] = foods

    if request.method == 'POST':

        if 'card_id' in request.form:
            # Retreive entry ID (which should be the direct entry name)
            card_id = request.form.get('card_id')

            # Close button
            for entry in ENTRIES:
                if entry == card_id:
                    #ENTRIES.remove(entry)
                    entrynum = int(entry[5:]) - 1
                    dbusers.deleteEntry(netid, entrynum)
                    
                    # REFILL ENTRIES?
                    cursor = dbusers.finduser(netid)
                    entries_info = cursor['daily_rec']
                    ENTRIES = ["Entry " + str(i + 1) for i in range(len(entries_info))]
                    foods_lists = [entry[:] for entry in entries_info]

                    entries_food_dict = {}
                    for i in range(len(ENTRIES)):
                        entry = ENTRIES[i]
                        foods = foods_lists[i]
                        entries_food_dict[entry] = foods
                    break

            return render_template('editingplate.html', ampm=get_ampm(), netid=netid,
                    curr_caltotal=curr_caltotal, cal_goal=cal_goal,
                    entries_food_dict=entries_food_dict)
    

        elif 'save_plate' in request.form:
            # Save button action (update database)
    
            return redirect('/homepage')
    
    return render_template('editingplate.html', ampm=get_ampm(), netid=netid,
                           curr_caltotal=curr_caltotal, cal_goal=cal_goal,
                           entries_food_dict=entries_food_dict)

#--------------------------------------------------------------------

@app.route('/logfood', methods=['GET', 'POST'])
def log_food():
    netid = auth.authenticate()
    if request.method == 'POST':
        return redirect('/homepage')

    

    eastern = timezone('America/New_York')
    now_est = datetime.datetime.now(eastern)
    menu = dbmenus.query_menu_display(now_est, 'breakfast', 'Rockefeller & Mathey Colleges')
    if not menu:
        return render_template('logfood.html') 
    # Given the new data structure, mealtime/dhall pairs only have one corresponding document
    result = menu[0]
    food_list = []

    # Extend the food_items list with the keys from each dictionary
    for category in result['data'].values():
        food_list.extend(category.keys())

    return render_template('logfood.html', food_items = food_list)

#--------------------------------------------------------------------

@app.route('/logfood/data', methods=['GET'])
def log_food_data():
    dhall = request.args.get('dhall', type = str)
    mealtime = request.args.get('mealtime', type = str)
    print(f"dhall: {dhall}, mealtime: {mealtime}")

    current_date = datetime.datetime.today()
    current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)


    # query menu documents
    menus = dbmenus.query_menu_display(current_date_zeros, mealtime, dhall)

    print(menus)
    if not menus:
        return jsonify({"error": "No data found"}), 404
    result = menus[0]
   
    food_list = []

    # Extend the food_items list with the keys from each dictionary
    for category in result['data'].values():
        food_list.extend(category.keys())


    return jsonify(food_list)

#--------------------------------------------------------------------

@app.route('/logout', methods=['GET'])
def logoutcas():
    return auth.logoutcas()

#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='localhost', port=55556, debug=True)
