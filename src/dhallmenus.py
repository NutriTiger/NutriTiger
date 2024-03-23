import sys
import json

sys.path.append('./scraper')


from scraper import get_daily_menus_from_range, get_daily_menus
from dbmenus import update_menu
import datetime

def main():
    start_date = datetime.datetime(2024, 3, 19)
    end_date = datetime.datetime(2024, 3, 22)

    menu_items_list_range, _ = get_daily_menus_from_range(start_date, end_date)
    #menu_items_list_range, _ = get_daily_menus()
    print(type(menu_items_list_range))
    #json_object = json.dumps(menu_items_list_range, indent=4, default=str)
    #print(type(json_object))
    #with open("testrecipes.json", "w") as outfile:
    #    outfile.write(json_object)


    update_menu(menu_items_list_range)




if __name__ == "__main__":
    main()
