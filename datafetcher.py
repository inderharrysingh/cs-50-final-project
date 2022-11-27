import requests


def datasender(q, diet, health, cuisineType, mealType, dishType):
    header = {

        "type": "public",
        "app_id": "113839cf",
        "app_key": "ed51f70d5017e768b6e323be431bf610",
        "q": q,
        'diet': [diet],
        'health': [health],
        'cuisineType': [cuisineType],
        'mealType': [mealType],
        'dishType': [dishType]

    }

    request = requests.get("https://api.edamam.com/api/recipes/v2", params=header)
    request.raise_for_status()

    data = request.json()

    list = []

    for i in data['hits']:
        dict = {}
        # return name of all dishes
        dict['label'] = (i['recipe']['label'])

        # return uri of image
        dict['img'] = i['recipe']['images']['SMALL']['url']

        dict['img1'] = i['recipe']['images']['REGULAR']['url']
        dict['dish_id'] = i['recipe']['uri'].split('#')[1]

        # link of main website from where people can have recipe of dish
        dict['link'] = i['recipe']['shareAs']

        # returns name of the ingredients
        dict['ingredients'] = i['recipe']['ingredientLines']

        # returns how many calories it has
        dict['calories'] = f"{round(i['recipe']['calories'], 2)}cal"

        # return when this particular meal should be taken

        # return total nutrient content of the dish
        dict['sugar'] = f"{round(i['recipe']['totalNutrients']['SUGAR']['quantity'], 2)}g"
        dict['fat'] = f"{round(i['recipe']['totalNutrients']['FAT']['quantity'], 2)}g"

        list.append(dict)

    return list


def idsender(id):
    header = {
        "type": "public",
        "app_id": "113839cf",
        "app_key": "ed51f70d5017e768b6e323be431bf610",

    }

    request = requests.get(f"https://api.edamam.com/api/recipes/v2/{id}", params=header)
    request.raise_for_status()
    i = request.json()
    dict = {}
    # return name of all dishes
    dict['label'] = (i['recipe']['label'])

    # return uri of image
    dict['img'] = i['recipe']['images']['SMALL']['url']

    dict['img1'] = i['recipe']['images']['REGULAR']['url']
    dict['dish_id'] = i['recipe']['uri'].split('#')[1]

    # link of main website from where people can have recipe of dish
    dict['link'] = i['recipe']['shareAs']

    # returns name of the ingredients
    dict['ingredients'] = i['recipe']['ingredientLines']

    # returns how many calories it has
    dict['calories'] = f"{round(i['recipe']['calories'], 2)}cal"

    # return when this particular meal should be taken

    # return total nutrient content of the dish
    dict['sugar'] = f"{round(i['recipe']['totalNutrients']['SUGAR']['quantity'], 2)}g"
    dict['fat'] = f"{round(i['recipe']['totalNutrients']['FAT']['quantity'], 2)}g"

    return dict
