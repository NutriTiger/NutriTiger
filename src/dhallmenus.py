import sys
import json

sys.path.append('./scraper')


from scraperfast import get_daily_menus_from_range, get_daily_menus
from dbmenus import update_menu
import datetime
import asyncio

def main():
    start_date = datetime.datetime.today()
    start_date_zeros = datetime.datetime(start_date.year, start_date.month, start_date.day)
    end_date = start_date_zeros + datetime.timedelta(days=7)
    #start_date_str = start_date..strftime('%Y-%m-%d')
    #end_date_str = end_date.strftime('%Y-%m-%d')
    menu_items_list_range, _ = asyncio.run(get_daily_menus_from_range(start_date_zeros, end_date))
    #menu_items_list_range, _ = get_daily_menus()
    #json_object = json.dumps(menu_items_list_range, indent=4, default=str)
    #print(type(json_object))
    #with open("testrecipes.json", "w") as outfile:
    #    outfile.write(json_object)


    update_menu(menu_items_list_range)


if __name__ == "__main__":
    main()
