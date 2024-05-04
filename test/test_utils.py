import unittest
import datetime
from src.utils import *

class TestUtils(unittest.TestCase):

    def test_time_of_day_morning_weekday(self):
        date = datetime.datetime(2024, 3, 25)
        time = datetime.time(4, 0)
        self.assertEqual(time_of_day(date, time), 'Breakfast')

    def test_time_of_day_brunch_weekend(self):
        date = datetime.datetime(2024, 3, 23)
        time = datetime.time(4, 0)
        self.assertEqual(time_of_day(date, time), 'Lunch')

    def test_time_of_day_brunch_weekend_noon(self):
        date = datetime.datetime(2024, 3, 23)
        time = datetime.time(12, 0)
        self.assertEqual(time_of_day(date, time), 'Lunch')

    def test_time_of_day_brunch_weekend_normal(self):
        date = datetime.datetime(2024, 3, 23)
        time = datetime.time(1, 0)
        self.assertEqual(time_of_day(date, time), 'Lunch')

    def test_time_of_day_lunch_weekday(self):
        date = datetime.datetime(2024, 3, 26)
        time = datetime.time(12, 0)
        self.assertEqual(time_of_day(date, time), 'Lunch')

    def test_time_of_day_dinner_weekday_one(self):
        date = datetime.datetime(2024, 3, 26)
        time = datetime.time(14, 1)
        self.assertEqual(time_of_day(date, time), 'Dinner')

    def test_time_of_day_dinner_weekday_two(self):
        date = datetime.datetime(2024, 3, 26)
        time = datetime.time(19, 0)
        self.assertEqual(time_of_day(date, time), 'Dinner')

    def test_custom_date_string_first(self):
        date = datetime.datetime(2024, 3, 1)
        self.assertEqual(custom_strftime(date), 'Friday, March 1st')
    
    def test_custom_date_string_second(self):
        date = datetime.datetime(2024, 3, 2)
        self.assertEqual(custom_strftime(date), 'Saturday, March 2nd')
    
    def test_custom_date_string_third(self):
        date = datetime.datetime(2024, 3, 3)
        self.assertEqual(custom_strftime(date), 'Sunday, March 3rd')
    
    def test_custom_date_string_one(self):
        date = datetime.datetime(2024, 3, 7)
        self.assertEqual(custom_strftime(date), 'Thursday, March 7th')
    
    def test_custom_date_string_two(self):
        date = datetime.datetime(2024, 3, 11)
        self.assertEqual(custom_strftime(date), 'Monday, March 11th')

    def test_custom_date_string_three(self):
        date = datetime.datetime(2024, 3, 20)
        self.assertEqual(custom_strftime(date), 'Wednesday, March 20th')
    
    def test_custom_date_string_four(self):
        date = datetime.datetime(2024, 3, 21)
        self.assertEqual(custom_strftime(date), 'Thursday, March 21st')
    
    def test_is_weekend_is(self):
        date = datetime.datetime(2024, 3, 3)
        self.assertEqual(is_weekend(date), True)
    
    def test_is_weekend_not(self):
        date = datetime.datetime(2024, 3, 21)
        self.assertEqual(is_weekend(date), False)

    def test_gtocal(self):
        self.assertEqual(gtocal(2, 3, 4), (8, 27, 16))
    
    def test_get_corresponding_arrays(self):
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days = 1)
        today_month = today.month
        today_day = today.day
        yesterday_month = yesterday.month
        yesterday_day = yesterday.day

        if today_month < 10:
            today_month = "0" + str(today_month)
        if today_day < 10:
            today_day = "0" + str(today_day)
        if yesterday_month < 10:
            yesterday_month = "0" + str(yesterday_month)
        if yesterday_day < 10:
            yesterday_day = "0" + str(yesterday_day)

        today_string = str(today_month) + '-' + str(today_day)
        yesterday_string = str(yesterday_month) + '-' + str(yesterday_day)
        self.assertEqual(get_corresponding_arrays([8, 5], [27, 3], [16, 9], [4, 4]), ([8, 5], [27, 3], [16, 9], [4, 4], [today_string, yesterday_string]))

    def test_get_average_one(self):
        test_data = [1, 2, 3, 4, 5, 6]
        self.assertEqual(get_average(test_data, 2), 1.5)

    def test_get_average_two(self):
        test_data = [1, 6]
        self.assertEqual(get_average(test_data, 4), 3.5)
    
    def test_gather_recipes(self):
        test_data = [{'data': {'somedhall': {'recipeids': [123, 456]}}}, {'data': {'somedhall': {'recipeids': [789, 312]}}}]
        result = [[123, 456], [789, 312]]
        self.assertEqual(gather_recipes(test_data), result)

    def test_parse_nutritional_info(self):
        # Sample API response we might get. Only kept fields relevant for this function
        test_data = {"foods": [{"fdcId": 0,"description": "CARROTS","foodNutrients": [{"amount": 384,"unitName": "g",}],"ingredients": "some items"}]}
        self.assertEqual(parse_nutritional_info(test_data), [{'recipeid': 'usda-0', 'mealname': 'CARROTS', 'servingSize': '100g', 'ingredients': 'some items'}])

    def test_trim_data(self):
        test_data = [{"fdcId": 0,"description": "CARROTS","foodNutrients": [{"amount": 384,"unitName": "g",}],"ingredients": "some items"}]
        self.assertEqual(trim_data(test_data), [{'fdcId': 0, 'description': 'CARROTS', 'foodNutrients': [{'amount': 384, 'unitName': 'g'}], 'ingredients': 'some items'}])

    def test_check_nutrition_info(self):
        self.assertEqual(check_nutrition_info(300, 20, 10, 3), True)

    def test_normalize_space_one(self):
        test_input = "            te st        "
        self.assertEqual(normalize_space(test_input), "te st")

    def test_normalize_space_two(self):
        test_input = "test"
        self.assertEqual(normalize_space(test_input), "test")

if __name__ == '__main__':
    unittest.main()
