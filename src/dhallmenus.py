from scraperfast import get_daily_menus_from_range
from dbmenus import update_menu
from dbnutrition import update_nutrition
import datetime
import asyncio

def main():
    start_date = datetime.datetime.today()
    start_date_zeros = datetime.datetime(start_date.year, start_date.month, start_date.day)
    end_date = start_date_zeros + datetime.timedelta(days=14)
    menu_items_list_range, menu_items_nutrition_range = asyncio.run(get_daily_menus_from_range(start_date_zeros, end_date))


    update_menu(menu_items_list_range)
    print(menu_items_nutrition_range)
    update_nutrition(menu_items_nutrition_range)



if __name__ == "__main__":
    main()
