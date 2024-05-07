#-----------------------------------------------------------------------
# INSTRUCTIONS
# run with the command: python gradingscript.py netid
# where netid is the netid of the user you want to load history and 
# custom foods for, loads 100 days of history and whatever custom foods
# the TEMPLATE_USER has. 
# uncomment the clear_history line in main if you want to clear the 
# user history, rather than just append to it
#-----------------------------------------------------------------------
import dbusers
import dbnutrition
import dbfunctions
import random
import sys
#-----------------------------------------------------------------------
TEMPLATE_USER = "jm0278"
NUM_LOGGED_DAYS = 100
#-----------------------------------------------------------------------
def load_custom_foods(netid):
    custom_foods = dbnutrition.find_all_custom_nutrition(TEMPLATE_USER)
    keys_to_exclude = ["mealname", "access", "recipeid", "date", "_id"]
    for document in custom_foods:
        mealname = document["mealname"]
        nutrition = {key: value for key, value in document.items() if key not in keys_to_exclude}
        dbnutrition.add_custom_food(mealname, netid, nutrition)
#-----------------------------------------------------------------------
def load_history(netid):
    this_user = dbusers.finduser(netid)
    cal_his = this_user['cal_his']
    carb_his = this_user['carb_his']
    prot_his = this_user['prot_his']
    fat_his = this_user['fat_his']

    # load history based on certain percentage of calories going to carbs, fats, proteins
    for i in range(NUM_LOGGED_DAYS):
        num_cals = 2000 + random.randint(0, 1000)
        num_prot = round((0.3 * num_cals) / 4, 2)
        num_carb = round((0.5 * num_cals) / 4, 2)
        num_fat = round((0.2 * num_cals) / 9, 2)
        cal_his.append(num_cals)
        prot_his.append(num_prot)
        carb_his.append(num_carb)
        fat_his.append(num_fat)
    
    this_user['cal_his'] = cal_his
    this_user['carb_his'] = carb_his
    this_user['prot_his'] = prot_his
    this_user['fat_his'] = fat_his
    dbusers.__setuser__(netid, this_user)
#-----------------------------------------------------------------------
# clears the user history, including today's logged meals
def clear_history(netid):
    this_user = dbusers.finduser(netid)
    this_user['cal_his'] = [0]
    this_user['carb_his'] = [0]
    this_user['prot_his'] = [0]
    this_user['fat_his'] = [0]
    this_user['daily_rec'] = []
    this_user['daily_serv'] = []
    this_user['daily_nut'] = []
    dbusers.__setuser__(netid, this_user)
#-----------------------------------------------------------------------
def main():
    arguments = sys.argv
    if len(arguments) > 1:
        netid = arguments[1]
        # clear_history(netid)
        # dbusers.newuser(netid, 2000)
        # load_history(netid)
        load_custom_foods(netid)
#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()
