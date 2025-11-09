import pandas as pd
from pathlib import Path
import struct


try:
    #Try to read the extended recipes dataset
    recipes = pd.read_csv('data/recipes_extended.csv')
    ingredients = pd.DataFrame(columns=['id', 'name'])
    recipe_ingredients = pd.DataFrame(columns=['recipe_id', 'ingredient_id', 'measurement'])
        
except FileNotFoundError:
    print("The file 'data/recipes_extended.csv' was not found.")

RECIPE_STRUCT = struct.Struct("i120s50s500sii20s4?")manu
r = Path("data/recipes.bin")
r.parent.mkdir(parents=True, exist_ok=True)
total_recipes = 0 # Initialize recipe counter

INGREDIENT_STRUCT = struct.Struct("i70s")
i = Path("data/ingredients.bin")
i.parent.mkdir(parents=True, exist_ok=True)
total_ingredients = 0 # Initialize recipe counter

RECIPE_INGREDIENT_STRUCT = struct.Struct("iii70s")
ri = Path("data/ingredients.bin")
ri.parent.mkdir(parents=True, exist_ok=True)
max_ingredients = recipes['num_ingredients'].max() #Max ingredients per recipe
min_ingredients = recipes['num_ingredients'].min() #Min ingredients per recipe
media_ingredients = 0 #Average ingredients per recipe
total_time = 0 #Total time for all recipes

with open("recipes.bin", "wb") as f_recipes, open("ingredients.bin", "wb") as f_ingredients, open("recipe_ingredients.bin", "wb") as f_recipe_ingredients:

    # Functions to handle ingredients and their relations
    def add_ingredients(ingredients_list, ingreadients_measurement, recipe_id):
        global total_ingredients
        for a in range(len(ingredients_list)):
            if ingredients_list[a] not in ingredients['name'].values: # New ingredient
                total_ingredients += 1
                ingredient_id = len(ingredients) + 1
                ingredients.loc[len(ingredients)] = [ingredient_id, ingredients_list[a]]
                f_ingredients.write(INGREDIENT_STRUCT.pack( # Write ingredient to binary file
                    ingredient_id,
                    ingredients_list[a].encode('utf-8'),
                ))
                build_recipe_ingredient_relation(recipe_id, ingredient_id, ingreadients_measurement[a], ingredients_list[a])
        return

    # Function to build recipe-ingredient relation
    def build_recipe_ingredient_relation(recipe_id, ingredient_id, measurement, ingredient_name):
        index = measurement.find(ingredient_name)
        recipe_ingredients_id = len(recipe_ingredients) + 1
        recipe_ingredients.loc[len(recipe_ingredients)] = [recipe_id, ingredient_id, measurement[:index].strip()]
        f_recipe_ingredients.write(RECIPE_INGREDIENT_STRUCT.pack( # Write relation to binary file
            recipe_ingredients_id,
            recipe_id,
            ingredient_id,
            measurement[:index].strip().encode('utf-8'),
        ))
        return


    for row in recipes.itertuples(index=True):
        total_recipes += 1
        add_ingredients(row.ingredients_canonical, row.ingredients_raw, total_recipes)
        time = row.est_prep_time_min + row.est_cook_time_min
        total_time += time
        f_recipes.write(RECIPE_STRUCT.pack(
            total_recipes,
            row.recipe_title.encode('utf-8'),
            row.subcategory.encode('utf-8'),
            row.directions.encode('utf-8'),
            time,
            row.num_steps,
            row.difficulty.encode('utf-8'),
            row.is_vegan,
            row.is_vegetarian,
            row.is_dairy_free,
            row.is_gluten_free,
        ))
