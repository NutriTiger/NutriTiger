#----------------------------------------------------------------------
# Contributors:
# Jewel Merriman, Rishabh Jain
#
#----------------------------------------------------------------------
import datetime

def time_of_day(date, time):
    lunch_start = datetime.time(11, 0)       
    dinner_start = datetime.time(14, 0)
    is_weekend_var = is_weekend(date)

    if time > dinner_start:
         return 'Dinner'
    elif time > lunch_start:
        return 'Lunch'
    else:
        if is_weekend_var:
            return 'Lunch'
        else:
            return 'Breakfast'

def custom_strftime(date_obj):
    suffix = 'th' if 11 <= date_obj.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(date_obj.day % 10, 'th')
    return date_obj.strftime('%A, %B %d') + suffix

def is_weekend(date):
    day_of_week = date.weekday()
    return (day_of_week >= 5)

# returns calories of carbs, fats, proteins
def gtocal(carbs, fats, proteins):
    return carbs*4, fats*9, proteins*4

# returns average of array, ignoring zeroes
def get_average(array):
    len = 0
    sum = 0
    for el in array:
        if el != 0 and el is not None:
            sum = sum + el
            len = len + 1
    return sum/len

def main():
    # Unit testing checks of functions
    date = datetime.datetime(2024, 3, 25)
    time = datetime.time(4, 0)
    print(time_of_day(date, time) == 'Breakfast')

    date = datetime.datetime(2024, 3, 23)
    time = datetime.time(4, 0)
    print(time_of_day(date, time) == 'Lunch')

    date = datetime.datetime(2024, 3, 23)
    time = datetime.time(12, 0)
    print(time_of_day(date, time) == 'Lunch')

    date = datetime.datetime(2024, 3, 23)
    time = datetime.time(1, 0)
    print(time_of_day(date, time) == 'Lunch')
    
    date = datetime.datetime(2024, 3, 26)
    time = datetime.time(12, 0)
    print(time_of_day(date, time) == 'Lunch')

    date = datetime.datetime(2024, 3, 26)
    time = datetime.time(14, 1)
    print(time_of_day(date, time) == 'Dinner')

    date = datetime.datetime(2024, 3, 26)
    time = datetime.time(19, 0)
    print(time_of_day(date, time) == 'Dinner')
    return

if __name__ == "__main__":
    main()