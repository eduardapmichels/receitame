
import pickle
from pathlib import Path
from receitas.Btree.BTree import BTree, build_bptree_index
from receitas.Btree.Node import Node
from receitas.Btree.Key import Key
import struct
from receitas.structs import *
from receitas.utilitario.globals import TRIE, BT
from receitas.data_handler import add_ingredients, build_recipe_ingredient_relation
import re

import math

################################################
#LEITURA DA RECEITA
################################################
def get_recipe_instructions(recipe_id, file_path="receitas/data/recipes.bin"):
    with open(file_path, "rb") as f:
        offset = (recipe_id - 1) * RECIPE_STRUCT.size
        f.seek(offset)
        data = f.read(RECIPE_STRUCT.size)
        if not data:
            return None
        unpacked = RECIPE_STRUCT.unpack(data)
        return unpacked[2].decode("utf-8").strip("\x00")


def get_ingredient_name(ingredient_id, file="receitas/data/ingredients.bin"):
    with open(file, "rb") as f:
        offset = (ingredient_id - 1) * INGREDIENT_STRUCT.size
        f.seek(offset)
        data = f.read(INGREDIENT_STRUCT.size)
        if not data:
            return None
        iid, name = INGREDIENT_STRUCT.unpack(data)
        return name.decode("utf-8").strip("\x00")


def get_recipe_ingredients(recipe_id, file="receitas/data/recipe_ingredients.bin"):
    ingredients = []
    with open(file, "rb") as f:
        while True:
            data = f.read(RECIPE_INGREDIENT_STRUCT.size)
            if not data:
                break

            _id, rid, ing_id, measurement = RECIPE_INGREDIENT_STRUCT.unpack(data)

            if rid == recipe_id:
                # Decodifica o measurement e remove padding/zeros
                measurement_str = measurement.decode('utf-8').strip('\x00').strip()
                ingredients.append((get_ingredient_name(ing_id), measurement_str))

    return ingredients





###########################################################
#B+Tree
###########################################################
def get_recipes_page_bt(page=1, per_page=200, min_time=None, max_time=None):
    node = BT.root
    while not node.is_leaf:
        node = node.children[0]

    all_filtered = []  # ids filtrados

    while node:
        for key in node.nodes:
            if min_time is not None and key.time < min_time:
                continue
            if max_time is not None and key.time > max_time:
                total_results = len(all_filtered)
                total_pages = math.ceil(total_results / per_page)
                return total_pages, paginate(all_filtered, page, per_page), total_results

            for recipe_id in key.recipes:
                all_filtered.append(recipe_id)

        node = node.next

    # terminou a árvore inteira
    total_results = len(all_filtered)
    total_pages = math.ceil(total_results / per_page)
    return total_pages, paginate(all_filtered, page, per_page), total_results


########################################################
# Trie - tree
#########################################################

def get_recipes_page_trie(page=1, per_page=200):
    if TRIE is None:
        print("Erro: TRIE não foi carregada.")
    recipes = []
    count = 0
    start_index = (page - 1) * per_page
    end_index = page * per_page

    # primeiro conta total de receitas
    def count_dfs(node):
        cnt = 0
        if node.end:
            cnt += len(node.positions)
        for child in node.children.values():
            cnt += count_dfs(child)
        return cnt

    total_results = count_dfs(TRIE.root)
    total_pages = math.ceil(total_results / per_page)

    # agora pega apenas a página
    def dfs(node):
        nonlocal count
        if node.end:
            for recipe_id, _pos in node.positions:
                if start_index <= count < end_index:
                    title = get_recipe_title(recipe_id)
                    time = get_recipe_time(recipe_id)
                    recipes.append((time, recipe_id, title))
                count += 1
                if count >= end_index:
                    return True
        for char in sorted(node.children.keys()):
            if dfs(node.children[char]):
                return True
        return False

    dfs(TRIE.root)

    return total_pages, recipes, total_results
###################################################################
# Arquivos invertidos
###################################################################

def load_tag_ids(name, tag, index):
    data_path = Path(f"receitas/data/tags_data_{name}.bin")

    if tag not in index:
        return []

    count, offset = index[tag]

    with open(data_path, "rb") as f:
        f.seek(offset)
        ids = []
        for _ in range(count):
            raw = f.read(ID_STRUCT.size)
            rid = ID_STRUCT.unpack(raw)[0]
            ids.append(rid)
    
    return ids


def intersect_tags(tags, all_tags):
    """Retorna IDs que aparecem em todas as tags (modo AND)"""
    sets_of_ids = []

    for tag in tags:
        if tag not in all_tags:
            # tag não existe -> interseção vazia
            return set()

        data_path, count, offset = all_tags[tag]
        ids = set()
        with open(data_path, "rb") as f_data:
            f_data.seek(offset)
            for _ in range(count):
                rid_bytes = f_data.read(ID_STRUCT.size)
                rid = ID_STRUCT.unpack(rid_bytes)[0]
                ids.add(rid)
        sets_of_ids.append(ids)

    result = sets_of_ids[0]
    for s in sets_of_ids[1:]:
        result &= s

    return result



def load_all_cuisines():
    cuisines_path = Path("receitas/data/cuisines.bin")
    cuisines = []

    if not cuisines_path.exists():
        return []

    with open(cuisines_path, "rb") as f:
        while True:
            data = f.read(CUISINE_STRUCT.size)
            if not data:
                break
            cuisine_id, cuisine_name = CUISINE_STRUCT.unpack(data)
            cuisines.append(cuisine_name.decode("utf-8").strip('\x00'))

    return cuisines


#####################################################################
# Funções comuns
#####################################################################

def paginate(all_filtered, page, per_page):
    start = (page - 1) * per_page
    end = page * per_page

    page_items = all_filtered[start:end]
    result = []
    for recipe_id in page_items:
        time = get_recipe_time(recipe_id)
        title = get_recipe_title(recipe_id)
        result.append((time, recipe_id, title))

    return result





def get_recipe_title(recipe_id, file_path="receitas/data/recipes.bin"):
    with open(file_path, "rb") as f:
        offset = (recipe_id - 1) * RECIPE_STRUCT.size
        f.seek(offset)
        data = f.read(RECIPE_STRUCT.size)
        if not data:
            return None
        unpacked = RECIPE_STRUCT.unpack(data)
        title = unpacked[1].decode("utf-8").strip('\x00')
        return title
    

def get_recipe_time(recipe_id, file_path="receitas/data/recipes.bin"):
    with open(file_path, "rb") as f:
        offset = (recipe_id - 1) * RECIPE_STRUCT.size
        f.seek(offset)
        data = f.read(RECIPE_STRUCT.size)
        if not data:
            return None
        unpacked = RECIPE_STRUCT.unpack(data)
        return unpacked[3]  # tempo da receita


def parse_int(value):
    try:
        if value is None or value == "":
            return None
        return int(value)
    except:
        return None
    


def process_ingredients_form(ingredients_input):
    """
    Processa o input do formulário de ingredientes.
    Espera o formato: [quantidade] ingrediente, [quantidade] ingrediente, ...
    Retorna duas listas: nomes de ingredientes e medidas.
    """
    if not ingredients_input.strip():
        return None, None, "Nenhum ingrediente informado."

    ingredients_list = []
    ingredients_measurement = []

    # Separar por vírgula
    items = [item.strip() for item in ingredients_input.split(',') if item.strip()]

    for idx, item in enumerate(items, start=1):
        # Validar o formato [medida] ingrediente
        match = re.match(r'\[(.*?)\]\s*(.+)', item)
        if not match:
            return None, None, f"Erro no ingrediente #{idx}: '{item}'. Use o formato [quantidade] ingrediente."
        
        measure, name = match.groups()
        ingredients_list.append(name.lower())
        ingredients_measurement.append(measure.strip())  # só a medida

    return ingredients_list, ingredients_measurement, None

def save_recipe_to_bin(data):
    """
    Salva uma nova receita nos arquivos binários e atualiza TRIE e B+ Tree.
    data: dict com keys -> title, time, difficulty, ingredients, instructions
    """
    global BT
    global TRIE
    # Caminhos para arquivos binários
    r_path = Path("receitas/data/recipes.bin")
    i_path = Path("receitas/data/ingredients.bin")
    ri_path = Path("receitas/data/recipe_ingredients.bin")

    r_path.parent.mkdir(parents=True, exist_ok=True)
    i_path.parent.mkdir(parents=True, exist_ok=True)
    ri_path.parent.mkdir(parents=True, exist_ok=True)

    # Carregar IDs atuais
    ingredients = {}
    total_ingredients = 0
    recipe_ingredients = 0
    total_recipes = 0

    if i_path.exists():
        with open(i_path, "rb") as f:
            while True:
                bytes_read = f.read(INGREDIENT_STRUCT.size)
                if not bytes_read:
                    break
                ingredient_id, name = INGREDIENT_STRUCT.unpack(bytes_read)
                ingredients[name.decode("utf-8").strip()] = ingredient_id
                total_ingredients = max(total_ingredients, ingredient_id)

    if r_path.exists():
        with open(r_path, "rb") as f:
            while True:
                bytes_read = f.read(RECIPE_STRUCT.size)
                if not bytes_read:
                    break
                recipe_id = RECIPE_STRUCT.unpack(bytes_read)[0]
                total_recipes = max(total_recipes, recipe_id)

    # Nova receita
    total_recipes += 1
    recipe_id = total_recipes

    # Processar ingredientes
    ingredients_list = []
    ingredients_measurement = []
    pattern = r'\[(.*?)\]\s*(.*?)(?:,|$)'
    matches = re.findall(pattern, data['ingredients'])
    for measure, name in matches:
        ingredients_list.append(name.strip().lower())
        ingredients_measurement.append(f"[{measure.strip()}] {name.strip()}")

    # Salvar nos arquivos binários
    with open(r_path, "ab") as f_recipes, open(i_path, "ab") as f_ingredients, open(ri_path, "ab") as f_recipe_ingredients:
        total_ingredients, recipe_ingredients = add_ingredients(
            ingredients_list,
            ingredients,
            ingredients_measurement,
            recipe_id,
            total_ingredients,
            recipe_ingredients,
            f_ingredients,
            f_recipe_ingredients,
            INGREDIENT_STRUCT,
            RECIPE_INGREDIENT_STRUCT
        )

        # Escrever a receita
        offset = f_recipes.tell()  # posição atual no arquivo para referência na trie
        f_recipes.write(RECIPE_STRUCT.pack(
            recipe_id,
            data['title'].encode('utf-8'),
            data['instructions'].encode('utf-8'),
            int(data['time']),
            data['difficulty'].encode('utf-8'),
            False,  # is_vegan
            False,  # is_vegetarian
            False,  # is_dairy_free
            False,  # is_gluten_free
            recipe_ingredients  # id da 1° relação receita-ingrediente
        ))

    # Atualizar TRIE e B+ Tree incrementalmente
    TRIE.insert(data['title'].lower(), recipe_id, offset)
    BT = BTree(50)
    BT=build_bptree_index(BT)
    
    index_path =  Path("receitas/data/trie.bin")
    with index_path.open("wb") as f:
        pickle.dump(TRIE, f)

    print("Tempo gravado:", data['time'])
    print("Tempo lido:", get_recipe_time(recipe_id))

    index_path =  Path("receitas/data/bptree.bin")

    with index_path.open("wb") as f:
        pickle.dump(BT, f)
    return f"Receita '{data['title']}' adicionada com sucesso!"
