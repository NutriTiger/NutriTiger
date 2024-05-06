#-----------------------------------------------------------------------
# This is the menu script/"cron job" that we run once a week to gather
# data and upload to our mongoDB database.
# INSTRUCTIONS
# run with the command: python src/menuscript.py
#-----------------------------------------------------------------------
from scraperfast import get_daily_menus_from_range
from dbmenus import update_menu
from dbnutrition import update_nutrition
import datetime
import asyncio

def main():
    # gets today's date and "zeros" it to the attributes we care about
    start_date = datetime.datetime.today()
    start_date_zeros = datetime.datetime(start_date.year, start_date.month, start_date.day)

    # change days= to the number of days in the future that you want to scrape for
    end_date = start_date_zeros + datetime.timedelta(days=14)
    # runs the fast scraper
    menu_items_list_range, menu_items_nutrition_range = asyncio.run(get_daily_menus_from_range(start_date_zeros, end_date))

    # uploads to database and prints out for the user to confirm
    update_menu(menu_items_list_range)
    print(menu_items_nutrition_range)
    update_nutrition(menu_items_nutrition_range)

if __name__ == "__main__":
    main()
