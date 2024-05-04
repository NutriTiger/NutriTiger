# ----------------------------------------------------------------------
# 
# app.py
#
# ----------------------------------------------------------------------

# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')
path.append('src/db')
from flask import Flask, render_template, request, redirect, make_response, jsonify, session, url_for, flash, send_file, Response
import time
import datetime
import os
import dotenv
import pytz
from pytz import timezone
#from CASClient import CASClient
from src import dbusers
from src import dbmenus
from src import dbnutrition
from src import dbfunctions
from src import utils
from src import auth
from src import photos
import requests
import json
from bson.objectid import ObjectId
from PIL import Image
from bson.binary import Binary
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename


#--------------------------------------------------------------------

app = Flask(__name__)
dotenv.load_dotenv()
app.secret_key = os.environ['APP_SECRET_KEY']
# Configuration
cloudinary.config(
    cloud_name = "cloud_name", 
    api_key = "api_key", 
    api_secret = "api_secret"
)

# Takes the user to a general error page if an error occurs
@app.errorhandler(Exception)
def not_found(e):
  session["error"] = str(e)
  print(e)
  return redirect("/error")

@app.route('/error', methods=['GET'])
def display_error():
    netid = auth.authenticate()
    error = session.pop("error")
    error404 = False
    if "404" in error:
        error404 = True
    return render_template("error.html", error=error, error404=error404)

#--------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    #netid = auth.authenticate()
    # Check if it is a user's first visit
    visited_before = session.get('username')

    if visited_before is None:
        # Indicate first contact
        # Set cookie to mark user as visited now
        #response = make_response(redirect('/welcome'))
        #response.set_cookie('visited_before', 'True')
        return render_template('index.html')
    
    return redirect('/homepage')

#--------------------------------------------------------------------

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    netid = auth.authenticate()
    
    cursor = dbusers.userlogin(netid)
    if cursor is None:
        return redirect('/welcome')
    
    curr_prots = round(float(cursor['prot_his'][0]), 1)
    curr_carbs = round(float(cursor['carb_his'][0]), 1)
    curr_fats = round(float(cursor['fat_his'][0]), 1)

    curr_caltotal = round(float(cursor['cal_his'][0]), 1)
    cal_goal = int(cursor['caloricgoal'])

    # A list of lists: holds recipeids for each entry
    entries_info = cursor['daily_rec']
    user_info = cursor['daily_nut']
    serv_info = cursor['daily_serv'] # List of lists of servings for each entry


    # Entry title strings array ("Meal #")
    ENTRIES = ["Meal " + str(i + 1) for i in range(len(entries_info))]

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
            
    # Add servings for each food
    servs_lists = []
    for entry in serv_info:


        entry_servings = entry[:]


        servings = []
        for serv in entry_servings:
            servings.append(serv)
       
        servs_lists.append(servings)

    # Create dict to pass in: match up ENTRIES list with foods_lists list
    entries_food_dict = {}
    for i in range(len(ENTRIES)):
        entry = ENTRIES[i]
        foods = foods_lists[i]
        totals = user_info[i]
        servings = servs_lists[i]
        entries_food_dict[entry] = {"foods": foods, "nutrition_totals": totals, "servings" : servings}

    # When Edit Plate button is pressed
    if request.method == 'POST':
        if 'add_entry' in request.form:
            return redirect('/logmeals')
        
        if 'historyBtn' in request.form:
            return redirect('/history')
        
        return redirect('/editingplate')

    return render_template('homepage.html', 
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
    mealtime = utils.time_of_day(current_date.date(), current_date.time())
    is_weekend_var = utils.is_weekend(current_date.now(timezone('US/Eastern')))
    
   
    todays_date = utils.custom_strftime(current_date)

    return render_template('menus.html', todays_date=todays_date, is_weekend_var=is_weekend_var, mealtime=mealtime, current_date=current_date)

@app.route('/menus/update', methods=['GET'])
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
        return render_template("menus_none.html", todays_date=todays_date, is_weekend_var=is_weekend_var)

    
    recipeids = utils.gather_recipes(data)
    nutrition_info = dbnutrition.find_many_nutrition(recipeids)

    DHALLS = ["Rockefeller & Mathey Colleges",
                        "Forbes College", "Graduate College",
                        "Center for Jewish Life",
                        "Yeh & New West Colleges",
                        "Whitman & Butler Colleges"]
    MEALTIMES = []
    if is_weekend_var:
        MEALTIMES = ["Lunch", "Dinner"]
    else:
        MEALTIMES = ["Breakfast", "Lunch", "Dinner"]

    missingdata = []
    for dhall in DHALLS:
        for meal in MEALTIMES:
            # Credit: https://stackoverflow.com/questions/52226293/jinja2-check-if-value-exists-in-list-of-dictionaries
            contains = [item['dhall'] == dhall and meal in item['mealtime'] for item in data]
            if True in contains:
                continue
            else:
                missingdata.append({'dhall': dhall, 'mealtime': meal})

    return render_template('menus_update.html', todays_date=todays_date, data=data, missingdata=missingdata,
                        nutrition_info=nutrition_info, is_weekend_var=is_weekend_var, mealtime=mealtime)

#--------------------------------------------------------------------

@app.route('/welcome', methods=['GET', 'POST'])
def first_contact():
    netid = auth.authenticate()
    if dbusers.finduser(netid) is not None:
        return redirect('/homepage')
    
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

    return render_template('welcome.html')

#--------------------------------------------------------------------

@app.route('/history', methods=['GET', 'POST'])
def history():
    netid = auth.authenticate()
    cursor = dbusers.userlogin(netid)
    if cursor is None:
        return redirect('/welcome')
    # find current user
    profile = dbusers.finduser(netid)
    cals, carbs, prots, fats, dates = utils.get_corresponding_arrays(profile['cal_his'], 
                                                                    profile['carb_his'],
                                                                    profile['prot_his'],
                                                                    profile['fat_his']
                                                                    )
    
    # Default range of history shown = 7
    his_range = 7

    # If user selects a different range, update his_range value
    if request.method == 'POST':
        data = request.get_json()
        selected_range = int(data.get("selectedRange"))
        his_range = selected_range
        cal_his = cals[:his_range]
        carb_his = carbs[:his_range]
        fat_his = fats[:his_range]
        prot_his = prots[:his_range]
        dates = dates[:his_range]

        avg_cals = utils.get_average(cal_his, his_range)
        avg_carbs = utils.get_average(carb_his, his_range)
        avg_pro = utils.get_average(prot_his, his_range)
        avg_fat = utils.get_average(fat_his, his_range)
        dates.reverse()
        cal_his.reverse()
        carb_his.reverse()
        prot_his.reverse()
        fat_his.reverse()

        html_code = render_template('history_content.html', 
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
        return make_response(html_code)
    
    else:

        cal_his = cals[:his_range]
        carb_his = carbs[:his_range]
        fat_his = fats[:his_range]
        prot_his = prots[:his_range]
        dates = dates[:his_range]

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

# Get image
# Get image
@app.route('/image/<image_id>')
def serve_image(photo_id):
    netid = auth.authenticate()
    
    # Load environment variables where your Cloudinary config is stored
    dotenv.load_dotenv()
    ccloud_name = os.getenv('cloud_name')
    capi_key = os.getenv("api_key")
    c_secret = os.getenv("api_secret")

    # Configure Cloudinary
    cloudinary.config( 
        cloud_name = ccloud_name, 
        api_key = capi_key, 
        api_secret = c_secret 
    )

    # Generate the URL of the image
    image_url, options = cloudinary.utils.cloudinary_url(photo_id)

    if not image_url:
        return jsonify({"error": "Image not found"}), 404


#--------------------------------------------------------------------

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    netid = auth.authenticate()
    cursor = dbusers.userlogin(netid)
    if cursor is None:
        return redirect('/welcome')
    if request.method == 'POST':
        #netid = 'jm0278'
        new_user_goal = request.form['line']
        dbusers.updategoal(netid, new_user_goal)
        return redirect('/homepage')
    user_settings = dbusers.findsettings(netid)
    current_cal_goal = user_settings['caloricgoal']
    join_date = utils.custom_strftime(user_settings['join_date'])
    user_nutrition = dbnutrition.find_all_custom_nutrition(netid)    

    return render_template('settings.html', netid=netid, current_cal_goal=current_cal_goal, join_date=join_date, user_nutrition=user_nutrition)

#--------------------------------------------------------------------


@app.route('/addingnutrition', methods=['POST'])
def add_usda_nutrition():
    netid = auth.authenticate()  # Authentication to identify the user

    if request.method == 'POST':
        try:
            data = request.get_json()

            new_data = data.get("nutritionData")
            
            if not new_data:
                return jsonify({'error': 'No data provided'}), 400
            
            dbnutrition.update_nutrition(new_data)

            return jsonify({'message': 'Nutrition data successfully added'}), 200
        except Exception as e:
            # Handle exceptions that may occur during the process
            return jsonify({'error': str(e)}), 500

    # Method not allowed
    return jsonify({'error': 'Invalid method'}), 405


#--------------------------------------------------------------------

@app.route('/editingplate', methods=['GET', 'POST'])
def editing_plate():
    netid = auth.authenticate()
    cursor = dbusers.userlogin(netid)
    if cursor is None:
        return redirect('/welcome')
    if request.method=='GET':
        cursor = dbusers.finduser(netid)
        daily_rec = cursor['daily_rec']
        daily_serv = cursor['daily_serv']
        entry_info = {}
        for entrynum, recids in enumerate(daily_rec):
            nutrition_info = dbnutrition.find_many_nutrition(recids)
            entry_info[entrynum] = zip(nutrition_info, daily_serv[entrynum])
        return render_template('editingplate.html',
                           entry_info = entry_info)
    else:
        # Unpack AJAX call 
        data = request.get_json()
        entriesToDel = data.get("entriesToDelete", [])
        foodsToDel = data.get("foodsToDelete", [])
        servingsToChange = data.get("servingsToChange", {})
        # delete entries/foods from user DB
        dbusers.editPlateAll(netid, entriesToDel, foodsToDel, servingsToChange)
        return jsonify({"success": True, "redirect": url_for('homepage')})

#--------------------------------------------------------------------

@app.route('/logmeals', methods=['GET', 'POST'])
def log_food():
    ENTRY_LIMIT = 50
    FOOD_LIMIT = 50
    netid = auth.authenticate()
    cursor = dbusers.userlogin(netid)
    if cursor is None:
        return redirect('/welcome')
    current_date = datetime.datetime.now(timezone('US/Eastern'))
    calc_mealtime = utils.time_of_day(current_date.date(), current_date.time())
    num_entries = len(cursor['daily_rec'])
    over_limit = num_entries >= ENTRY_LIMIT
    # Handle upload plate and return button
    if request.method == 'POST':
        # retrieve json object
        data = request.get_json()
        if not data or 'entry_recids' not in data or 'entry_servings' not in data:
            return jsonify({"success": False, "message": "Missing data"}), 400
        entry_recids = data.get('entry_recids')
        entry_servings = data.get('entry_servings')
        entry_nutrition = data.get('entry_nutrition')
        dbusers.addEntry(netid, {"recipeids": entry_recids, "servings": entry_servings, "nutrition": entry_nutrition})
        return jsonify({"success": True, "redirect": url_for('homepage')})
    else :
        current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
        is_weekend_var = utils.is_weekend(current_date.now(timezone('US/Eastern')))
    
        data = dbmenus.query_menu_display(current_date_zeros)
        recipeids = utils.gather_recipes(data)
        nutrition_info = dbnutrition.find_many_nutrition(recipeids)
    
        custom_data = dbnutrition.find_all_custom_nutrition(netid)
        if custom_data is None:
            custom_data = []
        items_per_page = 7
        total_pages = (int)(len(custom_data) / items_per_page)

        return render_template('logmeals.html', is_weekend_var = is_weekend_var, data=data, 
                                nutrition_info=nutrition_info, calc_mealtime = calc_mealtime, 
                                custom_data = custom_data, over_limit = str(over_limit).lower(), food_limit = FOOD_LIMIT, entry_limit = ENTRY_LIMIT, total_pages = total_pages)

#--------------------------------------------------------------------

@app.route('/logmeals/data', methods=['GET'])
def log_food_data():
    netid = auth.authenticate()

    current_date = datetime.datetime.now(timezone('US/Eastern'))
    current_date_zeros = datetime.datetime(current_date.year, current_date.month, current_date.day)
    is_weekend_var = utils.is_weekend(current_date.date())

    data = dbmenus.query_menu_display(current_date_zeros)
    recipeids = utils.gather_recipes(data)
    nutrition_info = dbnutrition.find_many_nutrition(recipeids)


    return render_template('logmeals_checkbox.html', data=data,
                        nutrition_info=nutrition_info, is_weekend_var=is_weekend_var)

@app.route('/logmeals/usdadata', methods=['GET'])
def logmeals_usdadata():
    netid = auth.authenticate()
    query = request.args.get('query', default="", type=str)
    dotenv.load_dotenv()
    api_key = os.getenv('usda_api_key')  # API key
    limit = 25

    # Construct the USDA API URL
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}&pageSize={limit}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()  # Convert response to JSON

        # Packs everything correctly
        parsed_data = utils.parse_nutritional_info(data)

        return jsonify(parsed_data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

#--------------------------------------------------------------------

@app.route('/customfoods', methods=['GET', 'POST'])
def custom_nutrition():
    netid = auth.authenticate()
    cursor = dbusers.userlogin(netid)
    if cursor is None:
        return redirect('/welcome')
    if request.method == 'POST':
        data = request.get_json()
        deletedFood = data.get('deletedFood')
        this_user = dbusers.handleDeletePersonalNutrition(netid, deletedFood)
        result = dbnutrition.del_custom_food(deletedFood)
        if result:
            return jsonify({"success": True, "redirect": url_for('custom_nutrition')})
        # IF THERE IS AN ERROR WITH THE DELETION: let's see if any issues come up
        # flash("Failed to delete custom food item(s).")
        return redirect(url_for('custom_nutrition'))

    else:
        user_nutrition = dbnutrition.find_all_custom_nutrition(netid)
        return render_template('custom_nutrition.html', user_nutrition=user_nutrition, custom_strftime=utils.custom_strftime)
#--------------------------------------------------------------------

@app.route('/addcustomfood', methods=['GET'])
def custom_food():
    netid = auth.authenticate()

    form_data = session.pop('form_data', None) if 'form_data' in session else {
        'message': "Enter nutrition information for your own food items!"
    }
    return render_template('custom_food.html', **form_data) 

#--------------------------------------------------------------------

# Flashes an issue with the submission and returns the previously
# typed elements back into the input areas
def add_customfood_tryagain(message, recipename, cal, carbs, protein, fats, servingsize, desc):
    flash(message)
    
    # Store form data and message in session
    session['form_data'] = {
        'name': recipename,
        'calories': cal,
        'carbs': carbs,
        'proteins': protein,
        'fats': fats,
        'servingsize': servingsize,
        'desc': desc,
    }
    return redirect(url_for('custom_food'))

#--------------------------------------------------------------------

def check_upload (file):
    if file and file.filename:
        file.seek(0, os.SEEK_END)  # Go to the end of file
        file_size = file.tell()    # Get current position, i.e., size of file
        file.seek(0)               # Reset pointer to the beginning

        if file_size > 0:
            # Proceed with your upload
            correct_type, file_ext = photos.allowed_file(file.filename)
            correct_size = photos.allowed_size(file)
            if not correct_type:
                return "Invalid file type :("
            if not correct_size:
                return "Uploaded file exceeds 10 MB"
            else:
                return
        else:
            return "Uploaded file is empty"
    
#--------------------------------------------------------------------

@app.route('/addcustomfood', methods=['POST'])
def add_customfood():
    netid = auth.authenticate()

    temp_name = request.form.get('name', type = str)
    recipename = utils.normalize_space(temp_name)
    query_name = recipename.lower()
    cal = request.form.get('calories', type = int)
    protein = request.form.get('proteins', type = int)
    carbs = request.form.get('carbs', type = int)
    fats = request.form.get('fats', type = int)
    servingsize = request.form.get('servingsize', type = str)
    desc = request.form.get('description', type = str)

    file = request.files.get('image')

    # Sanitizing - Empty inputs will be 0
    protein = protein or 0
    carbs = carbs or 0
    fats = fats or 0
    cal = cal or 0

    # Validation - no repeat recipe names
    result = dbnutrition.find_one_custom_nutrition(netid, query_name)
    if result:
        message = "Oh no! A custom food item with this name already exists, please put a new name."
        return add_customfood_tryagain(message, recipename, cal, carbs, protein, fats, servingsize, desc)


    nutrition_dict = {
                    "calories": cal,
                    "proteins": protein,
                    "carbs": carbs,
                    "fats": fats,
                    "servingsize": servingsize,
                    "description": desc,
                    "check": query_name
                    }
    # If there is a file, upload image
    if file:
        message = check_upload(file)

        # Validation - photo
        if message:
            return add_customfood_tryagain(message, recipename, cal, carbs, protein, fats, servingsize, desc)

        # Continue uploading
        dotenv.load_dotenv()
        ccloud_name = os.getenv('cloud_name')
        capi_key = os.getenv("api_key")
        c_secret = os.getenv("api_secret")

        cloudinary.config( 
            cloud_name = ccloud_name, 
            api_key = capi_key, 
            api_secret = c_secret 
        )

        response = cloudinary.uploader.upload(file, folder='NutriTiger_custom_photos' )
        url = response.get('url')
        public_id = response.get('public_id')

        nutrition_dict = {
                        "calories": cal,
                        "proteins": protein,
                        "carbs": carbs,
                        "fats": fats,
                        "servingsize": servingsize,
                        "description": desc,
                        "image_url": url,
                        "public_id": public_id
                        }



    dbnutrition.add_custom_food(recipename, netid, nutrition_dict)
    return redirect(url_for('custom_nutrition'))
    
    
    
#--------------------------------------------------------------------

@app.route('/logoutapp', methods=['GET'])
def logoutapp():
    return auth.logoutapp()

@app.route('/logoutcas', methods=['GET'])
def logoutcas():
    return auth.logoutcas()

#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=55557, debug=True)
