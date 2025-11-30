import pandas as pd
from pathlib import Path
import struct
import json
import re
import time
from receitas.Btree.BTree import BTree
import pickle
from pathlib import Path
from receitas.alfabeto_index import TrieNode
from receitas.alfabeto_index import Trie
from receitas.alfabeto_index import build_alfabeto_index
from receitas.invertedIndex.binarysearchtree import BinarySearchTree



total_ingredients = 0 # Initialize recipe counter
total_recipes = 0 # Initialize recipe counter
total_cuisines = 0 # Initialize cuisine counter
total_subcategories = 0 # Initialize subcategory counter
media_ingredients = 0 #Average ingredients per recipe
recipe_ingredients = 0

def data_handler():
    start_time = time.time()
    global total_ingredients
    global total_recipes
    global total_cuisines 
    global total_subcategories 
    global media_ingredients 
    global recipe_ingredients 

    total_ingredients = 0 # Initialize recipe counter
    total_recipes = 0 # Initialize recipe counter
    total_cuisines = 0 # Initialize cuisine counter
    total_subcategories = 0 # Initialize subcategory counter
    media_ingredients = 0 #Average ingredients per recipe
    recipe_ingredients = 0
    bt = BTree(50) #Initialize B+Tree (time)

    


    RECIPE_STRUCT = struct.Struct("i120si5500si20s4?i")
    r = Path("data/recipes.bin")
    r.parent.mkdir(parents=True, exist_ok=True)


    INGREDIENT_STRUCT = struct.Struct("i130s")
    i = Path("data/ingredients.bin")
    i.parent.mkdir(parents=True, exist_ok=True)

    CUISINE_STRUCT = struct.Struct("i130s")
    c = Path("data/cuisines.bin")
    c.parent.mkdir(parents=True, exist_ok=True)

    SUBCATEGORY_STRUCT = struct.Struct("i130s")
    s = Path("data/subcategories.bin")
    s.parent.mkdir(parents=True, exist_ok=True)


    RECIPE_INGREDIENT_STRUCT = struct.Struct("iii70s")
    ri = Path("data/recipe_ingredients.bin")
    ri.parent.mkdir(parents=True, exist_ok=True)

    RECIPE_CUISINE_STRUCT = struct.Struct("ii")
    rc = Path("data/recipe_cuisines.bin")
    rc.parent.mkdir(parents=True, exist_ok=True)

    media_ingredients = 0 #Average ingredients per recipe
    total_time = 0 #Total time for all recipes

    # Functions to handle ingredients and their relations
    def add_ingredients(ingredients_list, ingredients, ingredients_measurement, recipe_id):           
        global total_ingredients
        global recipe_ingredients
        for a in range(len(ingredients_list)):
            ingredients_list[a]= re.sub(r'^[^a-zA-ZÀ-ÿ]+', '', ingredients_list[a]) # Remove leading non-alphabetic characters
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
        return 0

    # Function to build recipe-ingredient relation
    def build_recipe_ingredient_relation(recipe_id, ingredient_id, measurement, ingredient_name, recipe_ingredients):
        index = measurement.find(ingredient_name[:3])
        measurement= measurement[:index].strip().encode('utf-8')
        f_recipe_ingredients.write(RECIPE_INGREDIENT_STRUCT.pack( # Write relation to binary file
            recipe_ingredients,
            recipe_id,
            ingredient_id,
            measurement,
        ))

        return 0


    # Function to handle cuisines
    def add_cuisines(recipe_id, cuisine_list):
        global total_cuisines
        for cuisine in cuisine_list:
            if cuisine not in cuisines: # New cuisine
                total_cuisines += 1
                cuisine_id = total_cuisines
                cuisines[cuisine] = cuisine_id
                f_cuisines.write(CUISINE_STRUCT.pack( # Write cuisine to binary file
                    cuisine_id,
                    cuisine.encode('utf-8'),
                ))
            else:
                cuisine_id = cuisines[cuisine]
            build_recipe_cuisine_relation(recipe_id, cuisine_id)
        return 0

    def build_recipe_cuisine_relation(recipe_id, cuisine_id):
        f_recipe_cuisines.write(RECIPE_CUISINE_STRUCT.pack( # Write relation to binary file
            recipe_id,
            cuisine_id,
        ))

        return 0

    # Function to handle subcategories
    def add_subcategories(recipe_id, subcategory):
        global total_subcategories
        if subcategory not in subcategories: # New subcategory
            total_subcategories += 1
            subcategory_id = total_subcategories
            subcategories[subcategory] = subcategory_id
            f_subcategories.write(SUBCATEGORY_STRUCT.pack(
                subcategory_id,
                subcategory.encode('utf-8')
            ))
        else:
            subcategory_id = subcategories[subcategory]

        return subcategory_id


    t0=time.time()

    recipes = None

    try:
        #Try to read the extended recipes dataset
        recipes = pd.read_csv('receitas/data/recipes_extended.csv')
        recipes['ingredients_canonical'] = recipes['ingredients_canonical'].str.lower()
        recipes['ingredients_canonical'] = recipes['ingredients_canonical'].apply(json.loads)
        recipes['ingredients_raw'] = recipes['ingredients_raw'].str.lower()
        recipes['ingredients_raw'] = recipes['ingredients_raw'].apply(json.loads)
        recipes['cuisine_list'] = recipes['cuisine_list'].str.lower()
        recipes['cuisine_list'] = recipes['cuisine_list'].apply(json.loads)
        recipes = recipes.drop_duplicates(subset=['recipe_title'])
        ingredients = {}
        cuisines = {}
        subcategories = {}
        
    except FileNotFoundError:
        
        print("The file 'data/recipes_extended.csv' was not found.")
        return {"total_recipes": 0, "time": 0, "message": "The file 'data/recipes_extended.csv' was not found."} 

        
    if recipes is None:
        return {"total_recipes": 0, "time": 0, "message":"The file 'data/recipes_extended.csv' was not found."}  # Evita erro
    

    tcsv = time.time()
    print(f"Time to read CSV: {tcsv-t0} seconds")

    t1 = time.time()
    with open(r, "wb") as f_recipes, open(i, "wb") as f_ingredients, open(ri, "wb") as f_recipe_ingredients, open(c, "wb") as f_cuisines, open(rc, "wb") as f_recipe_cuisines, open(s, "wb") as f_subcategories:
        for row in recipes.itertuples(index=True):
            total_recipes += 1
            add_ingredients(row.ingredients_canonical, ingredients, row.ingredients_raw, total_recipes)
            add_cuisines(total_recipes, row.cuisine_list)
            subcategory_id = add_subcategories(total_recipes, row.subcategory)
            time_recipe = row.est_prep_time_min + row.est_cook_time_min
            total_time += time_recipe
            bt.insert_key(time_recipe, total_recipes)
            id_relacao_ingrediente = recipe_ingredients
            f_recipes.write(RECIPE_STRUCT.pack(
                total_recipes,
                row.recipe_title.encode('utf-8'),
                subcategory_id,
                row.directions.encode('utf-8'),
                time_recipe,
                row.difficulty.encode('utf-8'),
                row.is_vegan,
                row.is_vegetarian,
                row.is_dairy_free,
                row.is_gluten_free,
                id_relacao_ingrediente          #id da 1° relação receita-ingrediente
            ))
    tbin = time.time()
    tend = time.time()
    total_elapsed = tend - start_time
    print(f"\n\n total receitas {total_recipes}")
    print(f"total ingredientes {total_ingredients}")
    print(f"cuisines {total_cuisines}")
    print(f"total subcategories {total_subcategories} \n\n")



    # dentro do data_handler, depois de construir bt
    pickle_path = Path("data/bptree.bin")
    pickle_path.parent.mkdir(parents=True, exist_ok=True)

    with open(pickle_path, "wb") as f:
        # protocol mais recente
        pickle.dump(bt, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    trie = Trie()
    build_alfabeto_index(trie)

    #Arquivos binarios
    # depois de percorrer o CSV e criar IDs
    bst_vegan = BinarySearchTree()
    bst_vegetarian = BinarySearchTree()
    bst_gluten_free = BinarySearchTree()
    bst_dairy_free = BinarySearchTree()
    bst_cuisines = BinarySearchTree()
    bst_difficulty = BinarySearchTree()

    # preenche as BSTs com os IDs já processados
    total_recipes = 0
    for recipe in recipes.itertuples():
        total_recipes += 1
        if recipe.is_vegan: bst_vegan.insert_recipe("vegan", total_recipes)
        if recipe.is_vegetarian: bst_vegetarian.insert_recipe("vegetarian", total_recipes)
        if recipe.is_gluten_free: bst_gluten_free.insert_recipe("gluten_free", total_recipes)
        if recipe.is_dairy_free: bst_dairy_free.insert_recipe("dairy_free", total_recipes)
        for cuisine in recipe.cuisine_list:
            bst_cuisines.insert_recipe(cuisine, total_recipes)
        bst_difficulty.insert_recipe(recipe.difficulty, total_recipes)

    # cria os arquivos invertidos
    bst_vegan.to_inverted_file("vegan")
    bst_vegetarian.to_inverted_file("vegetarian")
    bst_gluten_free.to_inverted_file("gluten_free")
    bst_dairy_free.to_inverted_file("dairy_free")
    bst_cuisines.to_inverted_file("cuisines")
    bst_difficulty.to_inverted_file("difficulty")



    return {"total_recipes": total_recipes, "time": total_elapsed, "message": "Success"}



   
