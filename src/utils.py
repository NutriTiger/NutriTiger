#----------------------------------------------------------------------
# Contributors:
# Jewel Merriman, Rishabh Jain
#
#----------------------------------------------------------------------
import datetime
# from datetime import datetime, timedelta
import pytz
import re

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

# returns the arrays: cal, carb, prot, fat, date
# where cal carb prot fat are all arrays with non-zero values
# and date is the corresponding date array for those entries
def get_corresponding_arrays(cal, carb, prot, fat):
    # generate date array
    eastern = pytz.timezone('US/Eastern')
    today = datetime.datetime.now(eastern).date()
    date_array = [today - datetime.timedelta(days=i) for i in range(len(cal))]
    # filter date and array for non-zero entries
    filtered_date_array = []
    filtered_cal_array = []

    for date_val, cal_val in zip(date_array, cal):
        if cal_val != 0:
            filtered_date_array.append(date_val.strftime('%m-%d'))
            filtered_cal_array.append(cal_val)
    filtered_carb_array = [x for x in carb if x != 0]
    filtered_prot_array = [x for x in prot if x != 0]
    filtered_fat_array = [x for x in fat if x != 0]
    return filtered_cal_array, filtered_carb_array, filtered_prot_array, filtered_fat_array, filtered_date_array

# returns average of array over the past ndays
# if length of array is less that ndays, just returns average of the array
def get_average(array, ndays):
    length = 0
    sum = 0
    if (len(array) > ndays):
        array = array[:ndays]
    for el in array:
        if el != 0:
            sum = sum + el
            length = length + 1
    if length == 0:
        return 0
    return sum/length

def gather_recipes(data):
    recipe_ids = []
    for entry in data:
        for meal_data in entry['data'].values():
            for recipe_id in meal_data.values():
                recipe_ids.append(recipe_id)
    return recipe_ids

# Organizes data --> less info to send + figure out serving size
def parse_nutritional_info(api_response):
    # Initialize an empty list to store the parsed food data
    foods = []
    meal_names = set()  # Set to track existing meal names to avoid duplicates
    
    # Loop through each food item in the response
    for food in api_response["foods"]:
        meal_name = food.get("description")
        # Check if mealName is already processed
        if meal_name in meal_names:
            continue  # Skip parsing this food item if mealName is a duplicate
        
        # Add the meal name to the set
        meal_names.add(meal_name)
        
        formatted_serving_size = "100g" if None in (food.get('servingSize'), food.get('servingSizeUnit')) else f"{round(int(food.get('servingSize')))} {food.get('servingSizeUnit')}"

        # Initialize a dictionary to store the information for each food item
        food_info = {
            "recipeid": 'usda-' + str(food.get("fdcId")),
            "mealname": meal_name,  # Use the description as meal name
            "servingSize": formatted_serving_size,  # Format the serving size
            "ingredients": food.get("ingredients", "No ingredients listed")  # Get ingredients if available
        }
        
        # Map nutrient names from the API to the desired keys
        nutrients_map = {
            "Energy": "calories",
            "Protein": "proteins",
            "Carbohydrate, by difference": "carbs",
            "Total lipid (fat)": "fats"
        }
        
        # Extract nutrient information
        for nutrient in food.get("foodNutrients", []):
            nutrient_name = nutrient.get("nutrientName")
            if nutrient_name in nutrients_map:
                # Map the nutrient value to the corresponding key in food_info
                food_info[nutrients_map[nutrient_name]] = round(int(nutrient.get("value")))
        
        # Append the parsed food item to the list
        foods.append(food_info)
    
    # Return the list of parsed food items
    return foods

def trim_data(data):
    new_data = {}
    
    for item in data:
        # Normalize the name to handle case sensitivity and spacing
        normalized_name = item["description"].strip().lower()

        # Check if the item already exists based on the normalized name
        if normalized_name not in new_data:
            new_data[normalized_name] = item
        else:
            # If a duplicate is found, keep the item with more nutritional data
            existing_item = new_data[normalized_name]
            if len(item.get('foodNutrients', [])) > len(existing_item.get('foodNutrients', [])):
                new_data[normalized_name] = item

    return list(new_data.values())

# ensures that the number of grams of proteins / carbs / fats
# is less than the calorie count
def check_nutrition_info(cal, protein, carbs, fats):
    total = 4*protein + 4*carbs + 9*fats
    print(total < cal)
    return (total < cal) | (total == cal) 


# Removes extra spaces and spaces at the front/back of the string
def normalize_space(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()

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