import pandas as pd
from pathlib import Path
import struct
import json
import re
import time
from receitas.Btree.BTree import BTree, build_bptree_index
import pickle
from pathlib import Path
from receitas.alfabeto_index import TrieNode
from receitas.alfabeto_index import build_alfabeto_index, Trie
from receitas.invertedIndex.binarysearchtree import BinarySearchTree
from receitas.structs import *
from receitas.utilitario.globals import *



#data_handler cria todo os dados binarios do site

#registra ingredientes novos em ingredients.bin
def add_ingredients(ingredients_list, ingredients, ingredients_measurement, recipe_id, total_ingredients, recipe_ingredients, f_ingredients, f_recipe_ingredients, INGREDIENT_STRUCT, RECIPE_INGREDIENT_STRUCT):           
    for a in range(len(ingredients_list)):
        #remove caracteres estranhos do incio
        ingredients_list[a]= re.sub(r'^[^a-zA-ZÀ-ÿ]+', '', ingredients_list[a]) 

        #se ingrediente nao existe cria
        if ingredients_list[a] not in ingredients:

            total_ingredients += 1
            ingredient_id = len(ingredients) + 1
            ingredients[ingredients_list[a]] = ingredient_id
            f_ingredients.write(INGREDIENT_STRUCT.pack( #
                
                ingredient_id,
                ingredients_list[a].encode('utf-8'),
            ))
        else:
            ingredient_id = ingredients[ingredients_list[a]]
        recipe_ingredients += 1
        #cria relacao ingrediente e receita
        #recipe_ingredients acumala as relacoes, é o id de das relacoes
        build_recipe_ingredient_relation(recipe_id, ingredient_id, ingredients_measurement[a], ingredients_list[a], recipe_ingredients,f_recipe_ingredients, RECIPE_INGREDIENT_STRUCT)
    return total_ingredients, recipe_ingredients

#grava um registro no recipe_ingredients.bin
def build_recipe_ingredient_relation(recipe_id, ingredient_id, measurement, ingredient_name, recipe_ingredients, f_recipe_ingredients, RECIPE_INGREDIENT_STRUCT):
    #separa parte medida do texto ex: medida é 2 cups
    index = measurement.find(ingredient_name[:3])
    measurement= measurement[:index].strip().encode('utf-8')
    f_recipe_ingredients.write(RECIPE_INGREDIENT_STRUCT.pack( # Write relation to binary file
        recipe_ingredients,
        recipe_id,
        ingredient_id,
        measurement,
    ))

    return 0

#cria cuisines.bin
def add_cuisines(total_cuisines, recipe_id, cuisine_list, cuisines, f_cuisines, f_recipe_cuisines, CUISINE_STRUCT, RECIPE_CUISINE_STRUCT):
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
        build_recipe_cuisine_relation(recipe_id, cuisine_id, f_recipe_cuisines, RECIPE_CUISINE_STRUCT)
    return total_cuisines
#cria relacao cuisines e recipes
def build_recipe_cuisine_relation(recipe_id, cuisine_id, f_recipe_cuisines, RECIPE_CUISINE_STRUCT):
    f_recipe_cuisines.write(RECIPE_CUISINE_STRUCT.pack( # Write relation to binary file
        recipe_id,
        cuisine_id,
    ))

    return 0

def data_handler():
    stats = {"start_time": time.time(),
    "total_ingredients": 0,
    "total_recipes":0,
    "total_cuisines":0,
    "media_ingredients":0,
    "recipe_ingredients":0,
    "media_ingredients":0,
    "total_time":0,
    }


    #cria caminhos
    r = Path("receitas/data/recipes.bin")
    r.parent.mkdir(parents=True, exist_ok=True)

    
    i = Path("receitas/data/ingredients.bin")
    i.parent.mkdir(parents=True, exist_ok=True)

    
    c = Path("receitas/data/cuisines.bin")
    c.parent.mkdir(parents=True, exist_ok=True)


    
    ri = Path("receitas/data/recipe_ingredients.bin")
    ri.parent.mkdir(parents=True, exist_ok=True)

    
    rc = Path("receitas/data/recipe_cuisines.bin")
    rc.parent.mkdir(parents=True, exist_ok=True)




    

    recipes = None

    try:
        #le csv
        recipes = pd.read_csv('receitas/data/recipes_extended.csv')
        #limpa e padroniza, cada celula vira uma losta pyhton
        recipes['ingredients_canonical'] = recipes['ingredients_canonical'].str.lower()
        recipes['ingredients_canonical'] = recipes['ingredients_canonical'].apply(json.loads)
        recipes['ingredients_raw'] = recipes['ingredients_raw'].str.lower()
        recipes['ingredients_raw'] = recipes['ingredients_raw'].apply(json.loads)
        recipes['cuisine_list'] = recipes['cuisine_list'].str.lower()
        recipes['cuisine_list'] = recipes['cuisine_list'].apply(json.loads)
        #remove receitas duplicadas
        recipes = recipes.drop_duplicates(subset=['recipe_title'])
        ingredients = {}
        cuisines = {}

        
      
    
                
    except FileNotFoundError:
        
        print("The file aaaaa'resipes/data/recipes_extended.csv' was not found.")
        stats["message"]="File not Found"
        return stats 

    #criacao arquivos.bin
    with open(r, "wb") as f_recipes, open(i, "wb") as f_ingredients, open(ri, "wb") as f_recipe_ingredients, open(c, "wb") as f_cuisines, open(rc, "wb") as f_recipe_cuisines:
        for row in recipes.itertuples(index=True):
            #salva ingredientes e relacoes
            id_relacao_ingrediente = stats["recipe_ingredients"]
            stats["total_recipes"] += 1       
            stats["total_ingredients"], stats["recipe_ingredients"]=add_ingredients(row.ingredients_canonical, ingredients, row.ingredients_raw, stats["total_recipes"], stats["total_ingredients"], stats["recipe_ingredients"],f_ingredients, f_recipe_ingredients, INGREDIENT_STRUCT, RECIPE_INGREDIENT_STRUCT)
            stats["total_cuisines"] = add_cuisines(stats["total_cuisines"],stats["total_recipes"], row.cuisine_list, cuisines, f_cuisines, f_recipe_cuisines, CUISINE_STRUCT, RECIPE_CUISINE_STRUCT)
            #calcula tempo total
            time_recipe = row.est_prep_time_min + row.est_cook_time_min
            stats["total_time"] += time_recipe
            
            #grava receita com a estrutua fixa
            #id
            #titulo
            #modo de prepato
            #tempo total
            #dificuldade
            #flags
            #id primeira relacao recipe_ingredents
            f_recipes.write(RECIPE_STRUCT.pack(
                stats["total_recipes"],
                row.recipe_title.encode('utf-8'),
                row.directions.encode('utf-8'),
                time_recipe,
                row.difficulty.encode('utf-8'),
                row.is_vegan,
                row.is_vegetarian,
                row.is_dairy_free,
                row.is_gluten_free,
                id_relacao_ingrediente          #id da 1° relação receita-ingrediente
            ))

                
    #Arquivos binarios
    # depois de percorrer o CSV e criar IDs
    bst_flags = BinarySearchTree()
    bst_cuisines = BinarySearchTree()
    bst_difficulty = BinarySearchTree()

    #cria 3 arvores BST com as flgs
    total_recipes = 0
    for recipe in recipes.itertuples():
        total_recipes += 1
        if recipe.is_vegan: bst_flags.insert_recipe("vegan", total_recipes)
        if recipe.is_vegetarian: bst_flags.insert_recipe("vegetarian", total_recipes)
        if recipe.is_gluten_free: bst_flags.insert_recipe("gluten_free", total_recipes)
        if recipe.is_dairy_free: bst_flags.insert_recipe("dairy_free", total_recipes)
        for cuisine in recipe.cuisine_list:
            bst_cuisines.insert_recipe(cuisine, total_recipes)
        bst_difficulty.insert_recipe(recipe.difficulty, total_recipes)

    # cria os arquivos invertidos
    bst_flags.to_inverted_file("flags")
    bst_cuisines.to_inverted_file("cuisines")
    bst_difficulty.to_inverted_file("difficulty")

    #constroe btree
    BT = BTree(50)
    BT=build_bptree_index(BT)
    
    #constroe trie
    TRIE = Trie()
    TRIE=build_alfabeto_index(TRIE)
    print(f'ingredientes: {stats["total_ingredients"]}, relações {stats["recipe_ingredients"]}, receitas {stats["total_recipes"]}')
    tend = time.time()
    #estatistica de retorno
    stats["finish_time"]=tend-stats["start_time"]
    stats["message"]=".csv lido com sucesso. Árvore B+ criada com sucesso. Arquivos invertidos criados com sucesso. Trie criada com sucesso"


    return stats
 

    