import re
import struct
import pickle
from pathlib import Path
from receitas.utilitario.globals import BT, TRIE  #arvores
from receitas.Btree import BTree
from receitas.alfabeto_index import Trie
from receitas.alfabeto_index import build_alfabeto_index
from receitas.data_handler import add_cuisines, add_ingredients, build_recipe_cuisine_relation, build_recipe_ingredient_relation
from receitas.structs import *


# -----------------------------
# Funções auxiliares
# -----------------------------

#salva qualquer estrutura de arvore, sempre que altera a trie/btree, salva aqui
def tree_to_bin(tree, path:str):
    pickle_path = Path(path)
    pickle_path.parent.mkdir(parents=True, exist_ok=True)

    with open(pickle_path, "wb") as f:
        pickle.dump(tree, f, protocol=pickle.HIGHEST_PROTOCOL)



#le arquivo ingredients.bin, se ingrediente ja existe cria novo ID
def load_ingredients_dict():

    ing_file = Path("receitas/data/ingredients.bin")
    ingredients = {}
    if not ing_file.exists():
        return ingredients

    with open(ing_file, "rb") as f:
        while True:
            data = f.read(INGREDIENT_STRUCT.size)
            if not data:
                break
            iid, name = INGREDIENT_STRUCT.unpack(data)
            name = name.decode().strip("\x00").strip()
            if name:
                ingredients[name] = iid

    return ingredients

#calcula prox id receita se recipes.bin tem 900 bytes e RECIPE_STRUCT.size = 300 bytes  900/300 = 3 receitas existentes, prox id = 4
def next_recipe_id():

    path = Path("receitas/data/recipes.bin")
    if not path.exists():
        return 1
    return path.stat().st_size // RECIPE_STRUCT.size + 1

#mesma logica  para relacao receia-ingrediente
def next_recipe_ingredient_id():
    """Calcula próximo ID da relação recipe_ingredient."""
    path = Path("receitas/data/recipe_ingredients.bin")
    if not path.exists():
        return 1
    return path.stat().st_size // RECIPE_INGREDIENT_STRUCT.size


# ------------------------------------------
# Função principal: adicionar receita nova
# ------------------------------------------


#chamada quando envia a receita no formulario HTML, pega os dados e junta num dicionario
def add_new_recipe(request):
    if request.method == "POST":
        title = request.POST.get("title")
        time_min = request.POST.get("time")
        difficulty = request.POST.get("difficulty")
        ingredients = request.POST.get("ingredients")
        instructions = request.POST.get("instructions")

        data = {
            "title": title,
            "time": time_min,
            "difficulty": difficulty,
            "ingredients": ingredients,
            "instructions": instructions
        }

        #salva recipes.bin, ingredients.bin, relacao e dps caha,a update dos indices 
        message = save_recipe_to_bin(data)
        return render(request, "add_recipe.html", {"message": message})

    return render(request, "add_recipe.html")

# ------------------------------------------
# Atualiza Trie + BTree
# ------------------------------------------

def update_indexes(rid, time_min, title, RECIPE_STRUCT, BT, TRIE, offset):
    # ---------- B+Tree ----------
    BT.insert_key(time_min, rid) #rid = id receita
    tree_to_bin(BT, "receitas/data/bptree.bin")

    # ---------- Trie ----------
    TRIE.insert(title.lower(), rid, offset)
    tree_to_bin(TRIE, "receitas/data/trie.bin")