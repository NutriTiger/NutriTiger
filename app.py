# ----------------------------------------------------------------------
# 
# app.py
#
# ----------------------------------------------------------------------

# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')
path.append('src/db')

from flask import Flask, render_template, request, redirect, make_response, jsonify, session, url_for
import time
import datetime
import os
import dotenv
from pytz import timezone
#from CASClient import CASClient
from src import dbusers
from src import dbmenus
from src import dbnutrition
from src import utils
from src import auth
import requests


#--------------------------------------------------------------------

app = Flask(__name__)
dotenv.load_dotenv()
app.secret_key = os.environ['APP_SECRET_KEY']
'''
# Takes the user to a general error page if an error occurs
@app.errorhandler(Exception)
def not_found(e):
  return redirect("/error")

@app.route('/error', methods=['GET'])
def display_error():
    netid = auth.authenticate()
    return render_template("error.html")
'''
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

    # will need to call whenever an existing user logs in
    cursor = dbusers.finduser(netid)
    curr_prots = round(float(cursor['prot_his'][0]), 1)
    curr_carbs = round(float(cursor['carb_his'][0]), 1)
    curr_fats = round(float(cursor['fat_his'][0]), 1)

    curr_caltotal = round(float(cursor['cal_his'][0]), 1)
    cal_goal = int(cursor['caloricgoal'])

    # A list of lists: holds recipeids for each entry
    entries_info = cursor['daily_rec']
    user_info = cursor['daily_nut']

    # Entry title strings array ("Entry #")
    ENTRIES = ["Entry " + str(i + 1) for i in range(len(entries_info))]

    # List of lists of foods, should match up with ENTRIES array
    foods_lists = []
    for entry in entries_info:

        entry_recipeids = entry[:]
    
        # Get nutrition info for entries
        entry_nutrition = dbnutrition.find_many_nutrition(entry_recipeids)

        # Check for None values in entry_nutrition (maybe ask Oyu to catch these in dbnutrition?)
        if entry_nutrition is None:
            foods_lists.append([])
        
        # If "mealname" for this recipeid, then add it to the list for current entry
        else:
            mealnames = []

            # For each food in the entry
            for food in entry_nutrition:
                if isinstance(food, dict) and "mealname" in food:
                    mealnames.append(food["mealname"])

            # Append the list of mealnames for this entry
            foods_lists.append(mealnames)
            
    # Create dict to pass in: match up ENTRIES list with foods_lists list
    entries_food_dict = {}
    for i in range(len(ENTRIES)):
        entry = ENTRIES[i]
        foods = foods_lists[i]
        totals = user_info[i]
        entries_food_dict[entry] = {"foods": foods, "nutrition_totals": totals}

    # When Edit Plate button is pressed
    if request.method == 'POST':
        return redirect('/editingplate')

    return render_template('homepage.html', 
                            ampm=get_ampm(), 
                            netid=netid,
                            prots=curr_prots,
                            carbs=curr_carbs,
                            fats=curr_fats,
                            curr_caltotal=curr_caltotal, 
                            cal_goal=cal_goal,
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
    current_date = datetime.datetime.now(timezone('US/Eastern'))
    #current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
    print(current_date.now(timezone('US/Eastern')))
    mealtime = utils.time_of_day(current_date.date(), current_date.time())
    is_weekend_var = utils.is_weekend(current_date.now(timezone('US/Eastern')))
    
   
    todays_date = utils.custom_strftime(current_date)
    #print(todays_date)

    return render_template('dhallmenus.html', todays_date=todays_date, is_weekend_var=is_weekend_var, mealtime=mealtime, current_date=current_date)

@app.route('/update-menus-mealtime', methods=['GET'])
def update_menus_mealtime():
    netid = auth.authenticate()
    current_date_string = request.args.get('currentdate')
    
    current_date = datetime.datetime.strptime(current_date_string, "%Y-%m-%d %H:%M:%S.%f%z")
    mealtime = request.args.get('mealtime')
    if mealtime:
        mealtime = utils.time_of_day(current_date.date(), current_date.time())

    #current_date = datetime.datetime.today()
    todays_date = utils.custom_strftime(current_date)

    current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
    is_weekend_var = utils.is_weekend(current_date.date())

    data = dbmenus.query_menu_display(current_date_zeros)
    if data == []:
        return render_template("dhallmenus_none.html", todays_date=todays_date, is_weekend_var=is_weekend_var)

    
    recipeids = utils.gather_recipes(data)
    nutrition_info = dbnutrition.find_many_nutrition(recipeids)

    #print(nutrition_info)

    #print(todays_date)

    return render_template('dhallmenus_update.html', todays_date=todays_date, data=data,
                        nutrition_info=nutrition_info, is_weekend_var=is_weekend_var, mealtime=mealtime)

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
    cals, carbs, prots, fats, dates = utils.get_corresponding_arrays(profile['cal_his'], 
                                                                    profile['carb_his'],
                                                                    profile['prot_his'],
                                                                    profile['fat_his']
                                                                    )
    his_range = 7 # THIS IS THE ONLY NUMBER WE NEED TO CHANGE FOR STRETCH
    cal_his = cals[:his_range]
    carb_his = carbs[:his_range]
    fat_his = fats[:his_range]
    prot_his = prots[:his_range]
    dates = dates[:7]

    avg_cals = utils.get_average(cal_his, his_range)
    avg_carbs = utils.get_average(carb_his, his_range)
    avg_pro = utils.get_average(prot_his, his_range)
    avg_fat = utils.get_average(fat_his, his_range)
    dates.reverse()
    cal_his.reverse()
    carb_his.reverse()
    prot_his.reverse()
    fat_his.reverse()

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
    user_settings = dbusers.findsettings(netid)
    current_cal_goal = user_settings['caloricgoal']
    join_date = user_settings['join_date']
    

    return render_template('settings.html', netid=netid, current_cal_goal=current_cal_goal, join_date=join_date)

#--------------------------------------------------------------------

@app.route('/editingplate', methods=['GET', 'POST'])
def editing_plate():
    netid = auth.authenticate()

    # Placeholder values
    #netid = 'jm0278' 
    cursor = dbusers.finduser(netid)
    curr_prots = round(float(cursor['prot_his'][0]), 1)
    curr_carbs = round(float(cursor['carb_his'][0]), 1)
    curr_fats = round(float(cursor['fat_his'][0]), 1)
    cal_goal = int(cursor['caloricgoal'])
    curr_caltotal = cursor['cal_his'][0]
    entries_info = cursor['daily_rec']

    # Testing filling the entries
    ENTRIES = ["Entry " + str(i + 1) for i in range(len(entries_info))]
    # A list of lists: holds recipeids for each entry
    entries_info = cursor['daily_rec']

    # Entry title strings array ("Entry #")
    ENTRIES = ["Entry " + str(i + 1) for i in range(len(entries_info))]

    # List of lists of foods, should match up with ENTRIES array
    foods_lists = []
    for entry in entries_info:

        entry_recipeids = entry[:]
    
        # Get nutrition info for entries
        entry_nutrition = dbnutrition.find_many_nutrition(entry_recipeids)

        # Check for None values in entry_nutrition (maybe ask Oyu to catch these in dbnutrition?)
        if entry_nutrition is None:
            foods_lists.append([])
        
        # If "mealname" for this recipeid, then add it to the list for current entry
        else:
            mealnames = []
            for meal in entry_nutrition:
                if isinstance(meal, dict) and "mealname" in meal:
                    mealnames.append(meal["mealname"])
            foods_lists.append(mealnames)

    # Create dict to pass in: match up ENTRIES list with foods_lists list
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

        elif 'add_entry' in request.form:
            return redirect('/logfood')

        elif 'save_plate' in request.form:
            # Save button action (update database)
    
            return redirect('/homepage')
    
    return render_template('editingplate.html', ampm=get_ampm(), netid=netid,
                           curr_caltotal=curr_caltotal, cal_goal=cal_goal,
                           entries_food_dict=entries_food_dict,
                           prots=curr_prots, carbs=curr_carbs, fats=curr_fats,)

#--------------------------------------------------------------------

@app.route('/logfood', methods=['GET', 'POST'])
def log_food():
    netid = auth.authenticate()
    # Handle upload plate and return button
    if request.method == 'POST':
        # retreive json object
        data = request.get_json()
        entry_recids = data.get('entry_recids')
        entry_servings = data.get('entry_servings')
        dbusers.addEntry(netid, {"recipeids": entry_recids, "servings": entry_servings})
        return jsonify({"success": True, "redirect": url_for('homepage')})
    else :
        current_date = datetime.datetime.now(timezone('US/Eastern'))
        current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
        is_weekend_var = utils.is_weekend(current_date.now(timezone('US/Eastern')))
    
        data = dbmenus.query_menu_display(current_date_zeros)
        print(data)
        recipeids = utils.gather_recipes(data)
        nutrition_info = dbnutrition.find_many_nutrition(recipeids)
        print("about to render template for logfood")

        return render_template('logfood.html', is_weekend_var = is_weekend_var, data=data, nutrition_info=nutrition_info)

#--------------------------------------------------------------------
@app.route('/logfood/myplate', methods=['GET'])
def log_food_myplate():
    checkid = request.args.get('checkid', type = str)
    mealname = request.args.get('mealname', type = str)
    recid = request.args.get('recid', type = int)
    location = request.args.get('location', type = str)
    mealtime = request.args.get('mealtime', type = str)
    servingsize = request.args.get('servingsize', type = str)
    cals = request.args.get('cals', type = float)
    prots = request.args.get('prots', type = float)
    carbs = request.args.get('carbs', type = float)
    fats = request.args.get('fats', type = float)
    uniqueid = checkid[8:]
    print(mealname, cals, prots, carbs, fats)

    html_code = render_template('myplateelements.html', checkid=checkid, uniqueid=uniqueid, mealname=mealname, 
                                recid=recid, location=location, mealtime=mealtime, servingsize=servingsize, 
                                cals=cals, prots=prots, carbs=carbs, fats=fats)
    return make_response(html_code)

@app.route('/logfood/data', methods=['GET'])
def log_food_data():
    netid = auth.authenticate()

    current_date = datetime.datetime.today()
    print(current_date)
    current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
    is_weekend_var = utils.is_weekend(current_date.date())

    data = dbmenus.query_menu_display(current_date_zeros)
    recipeids = utils.gather_recipes(data)
    nutrition_info = dbnutrition.find_many_nutrition(recipeids)


    return render_template('logfood_update.html', data=data,
                        nutrition_info=nutrition_info, is_weekend_var=is_weekend_var)

@app.route('/logfood/usdadata', methods=['GET'])
def logfood_usdadata():
    netid = auth.authenticate()
    query = request.args.get('query', default="", type=str)
    api_key = 'XBwD6rxHxWX1wTdECT9q778IWkDtNcxwkxOJECw9'  # API key

    # Construct the USDA API URL
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()  # Convert response to JSON
        return jsonify(data)  # Send JSON response back to client
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the HTTP request
        return jsonify({"error": str(e)}), 500
'''
@app.route('/logfood/data', methods=['GET'])
def log_food_data():
    dhall = request.args.get('dhall', type = str)
    mealtime = request.args.get('mealtime', type = str)
    print("we are inside logfood/data")
    print(f"dhall: {dhall}, mealtime: {mealtime}")

    # query menu documents
    current_date = datetime.datetime.today()
    current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
    menu = dbmenus.query_menu_display(current_date_zeros, mealtime, dhall)

    print(menu)
    if not menu:
        # return jsonify({"error": "No data found"}), 404
        data_found=False
        nut={}
    else:
        data_found=True
        result = menu[0]
        recids = []
        # Extend the food_items list with the keys from each dictionary
        for category in result['data'].values():
            for recid in category.values():
                recids.append(recid)
        nut = dbnutrition.find_many_nutrition(recids)
        print("FOOD ITEMS")
        print(nut)

    html_code = render_template('logfood_items.html', data_found=data_found, foods=nut)
    return make_response(html_code)
'''
#--------------------------------------------------------------------

@app.route('/personalfood', methods=['GET', 'POST'])
def personal_food():
    form_data = session.pop('form_data', None) if 'form_data' in session else {
        'name': "i.e. overnight oats", 'calories': 0, 'carbs': 0, 'proteins': 0, 'fats': 0, 'message': "Enter nutrition information for your own food items!"
    }
    return render_template('personalfood.html', **form_data) 

@app.route('/addpersonalfood', methods=['POST'])
def add_personal_food():
    netid = auth.authenticate()
    if request.method == 'POST':
        recipename = request.form.get('name', type = str)
        cal = request.form.get('calories', type = int)
        protein = request.form.get('proteins', type = int)
        carbs = request.form.get('carbs', type = int)
        fats = request.form.get('fats', type = int)
        nutrition_dict = {
                        "calories": cal,
                        "proteins": protein,
                        "carbs": carbs,
                        "fats": fats,
                        }
        result = dbnutrition.find_one_personal_nutrition(netid, recipename)
        if not result:
            dbnutrition.add_personal_food(recipename, netid, nutrition_dict)
            return redirect('/homepage')
        else:
            msg = "A personal food item with this name already exists, please put a new name!"
            # Store form data and message in session
            session['form_data'] = {
                'name': recipename,
                'calories': cal,
                'carbs': carbs,
                'proteins': protein,
                'fats': fats,
                'message': msg
            }
            return redirect(url_for('personal_food'))
        
    return
    
#--------------------------------------------------------------------

@app.route('/logout', methods=['GET'])
def logoutcas():
    return auth.logoutcas()

#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='localhost', port=55557, debug=True)
