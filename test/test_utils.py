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
        self.assertEqual(custom_strftime(date), 'Friday, March 01st')
    
    def test_custom_date_string_second(self):
        date = datetime.datetime(2024, 3, 2)
        self.assertEqual(custom_strftime(date), 'Saturday, March 02nd')
    
    def test_custom_date_string_third(self):
        date = datetime.datetime(2024, 3, 3)
        self.assertEqual(custom_strftime(date), 'Sunday, March 03rd')
    
    def test_custom_date_string_one(self):
        date = datetime.datetime(2024, 3, 7)
        self.assertEqual(custom_strftime(date), 'Thursday, March 07th')
    
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
        self.assertEqual(get_corresponding_arrays([8, 5], [27, 3], [16, 9], [4, 4]), ([8, 5], [27, 3], [16, 9], [4, 4], ['04-27', '04-26']))

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

if __name__ == '__main__':
    unittest.main()
