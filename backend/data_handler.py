import pandas as pd
from pathlib import Path
import struct
import json

total_ingredients = 0 # Initialize recipe counter
total_recipes = 0 # Initialize recipe counter

 # Functions to handle ingredients and their relations
def add_ingredients(ingredients_list, ingredients, ingredients_measurement, recipe_id):           
    global total_ingredients
    global recipe_ingredients
    for a in range(len(ingredients_list)):

        if ingredients_list[a] not in ingredients: # New ingredient
            total_ingredients += 1
            ingredient_id = len(ingredients) + 1
            ingredients[ingredients_list[a]] = ingredient_id
            f_ingredients.write(INGREDIENT_STRUCT.pack( # Write ingredient to binary file
                ingredient_id,
                ingredients_list[a].encode('utf-8'),
            ))
        else:
            ingredient_id = ingredients[ingredients_list[a]]
        recipe_ingredients += 1
        build_recipe_ingredient_relation(recipe_id, ingredient_id, ingredients_measurement[a], ingredients_list[a], recipe_ingredients)
    return

# Function to build recipe-ingredient relation
def build_recipe_ingredient_relation(recipe_id, ingredient_id, measurement, ingredient_name, recipe_ingredients):
    index = measurement.find(ingredient_name)
    f_recipe_ingredients.write(RECIPE_INGREDIENT_STRUCT.pack( # Write relation to binary file
        recipe_ingredients,
        recipe_id,
        ingredient_id,
        measurement[:index].strip().encode('utf-8'),
    ))
    return


try:
    #Try to read the extended recipes dataset
    recipes = pd.read_csv('data/recipes_extended.csv')
    recipes['ingredients_canonical'] = recipes['ingredients_canonical'].apply(json.loads)
    recipes['ingredients_raw'] = recipes['ingredients_raw'].apply(json.loads)
    recipes['cuisine_list'] = recipes['cuisine_list'].apply(json.loads)
    ingredients = {}
    recipe_ingredients = 0
except FileNotFoundError:
    print("The file 'data/recipes_extended.csv' was not found.")

RECIPE_STRUCT = struct.Struct("i120s50s5500si20s4?")
r = Path("data/recipes.bin")
r.parent.mkdir(parents=True, exist_ok=True)


INGREDIENT_STRUCT = struct.Struct("i70s")
i = Path("data/ingredients.bin")
i.parent.mkdir(parents=True, exist_ok=True)


RECIPE_INGREDIENT_STRUCT = struct.Struct("iii70s")
ri = Path("data/recipe_ingredients.bin")
ri.parent.mkdir(parents=True, exist_ok=True)

media_ingredients = 0 #Average ingredients per recipe
total_time = 0 #Total time for all recipes

with open("recipes.bin", "wb") as f_recipes, open("ingredients.bin", "wb") as f_ingredients, open("recipe_ingredients.bin", "wb") as f_recipe_ingredients:
    for row in recipes.itertuples(index=True):
        row = recipes.iloc[0]
        total_recipes += 1
        add_ingredients(row.ingredients_canonical, ingredients, row.ingredients_raw, total_recipes)
        time = row.est_prep_time_min + row.est_cook_time_min
        total_time += time
        f_recipes.write(RECIPE_STRUCT.pack(
            total_recipes,
            row.recipe_title.encode('utf-8'),
            row.subcategory.encode('utf-8'),
            row.directions.encode('utf-8'),
            time,
            row.difficulty.encode('utf-8'),
            row.is_vegan,
            row.is_vegetarian,
            row.is_dairy_free,
            row.is_gluten_free,
        ))


print(f"Total Recipes: {total_recipes}")
with open("recipes.bin", "rb") as f:
    for _ in range(15):
        bytes_lidos = f.read(RECIPE_STRUCT.size)
        if not bytes_lidos:
            break
        unpacked = RECIPE_STRUCT.unpack(bytes_lidos)

        recipe_id = unpacked[0]
        recipe_title = unpacked[1].decode('utf-8').rstrip('\x00')
        subcategory = unpacked[2].decode('utf-8').rstrip('\x00')
        directions = unpacked[3].decode('utf-8').rstrip('\x00')
        total_time = unpacked[4]
        difficulty = unpacked[5].decode('utf-8').rstrip('\x00')
        is_vegan, is_vegetarian, is_dairy_free, is_gluten_free = unpacked[6:]

        print(f"ID: {recipe_id}, Title: {recipe_title}, Subcategory: {subcategory}, Time: {total_time}, Difficulty: {difficulty}")

print(f"\n\nTotal Ingredients: {total_ingredients}")
with open("ingredients.bin", "rb") as f:
    for _ in range(5):
        bytes_lidos = f.read(INGREDIENT_STRUCT.size)
        if not bytes_lidos:
            break
        unpacked = INGREDIENT_STRUCT.unpack(bytes_lidos)
        ingredient_id = unpacked[0]
        ingredient_name = unpacked[1].decode('utf-8').rstrip('\x00')
        print(f"Ingredient ID: {ingredient_id}, Name: {ingredient_name}")

print(f"\n\nTotal Recipe-Ingredient Relations: {recipe_ingredients}")
with open("recipe_ingredients.bin", "rb") as f:
    for _ in range(5):
        bytes_lidos = f.read(RECIPE_INGREDIENT_STRUCT.size)
        if not bytes_lidos:
            break
        unpacked = RECIPE_INGREDIENT_STRUCT.unpack(bytes_lidos)
        relation_id, recipe_id, ingredient_id = unpacked[:3]
        measurement = unpacked[3].decode('utf-8').rstrip('\x00')
        print(f"Relation ID: {relation_id}, Recipe ID: {recipe_id}, Ingredient ID: {ingredient_id}, Measurement: {measurement}")
