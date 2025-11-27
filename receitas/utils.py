
import pickle
from pathlib import Path
from receitas.Btree.BTree import BTree
from receitas.Btree.Node import Node
from receitas.Btree.Key import Key
import struct

import math

def load_btree_pickle():
    p = Path("data/bptree.bin")
    if not p.exists():
        return None
    with open(p, "rb") as f:
        bt = pickle.load(f)
    
    root = bt.get_root()
    print(root.nodes[:root.n])
    return bt


def load_trie_pickle():
    p = Path("data/trie.bin")
    if not p.exists():
        return None
    with open(p, "rb") as f:
        trie = pickle.load(f)
    return trie

def get_recipes_page_trie(trie, page=1, per_page=200):
    all_ids = []

    # ---- DFS ORDENADO ----
    def dfs(node):
        if node.end:
            for recipe_id, _pos in node.positions:
                all_ids.append(recipe_id)

        # IMPORTANTE: garantir ordem alfabética por caractere
        for char in sorted(node.children.keys()):
            dfs(node.children[char])

    # faz varredura completa
    dfs(trie.root)

    # ---- CARREGA TODAS RECEITAS COM TÍTULO ----
    recipes = []
    for rid in all_ids:
        title = get_recipe_title(rid)
        time = get_recipe_time(rid)
        recipes.append((time, rid, title))

    # ---- ORDENA ALFABETICAMENTE PELO TÍTULO ----
    recipes.sort(key=lambda x: x[2].lower())

    # ---- PAGINA DEPOIS DE ORDENAR ----
    total_results = len(recipes)
    total_pages = math.ceil(total_results / per_page)

    start = (page - 1) * per_page
    end = page * per_page

    return total_pages, recipes[start:end], total_results


def get_recipes_page_bt(bt, page=1, per_page=200, min_time=None, max_time=None):
    node = bt.root
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





def get_recipe_title(recipe_id, file_path="data/recipes.bin"):
    RECIPE_STRUCT = struct.Struct("i120si5500si20s4?i")
    with open(file_path, "rb") as f:
        offset = (recipe_id - 1) * RECIPE_STRUCT.size
        f.seek(offset)
        data = f.read(RECIPE_STRUCT.size)
        if not data:
            return None
        unpacked = RECIPE_STRUCT.unpack(data)
        title = unpacked[1].decode("utf-8").strip('\x00')
        return title
    

def get_recipe_time(recipe_id, file_path="data/recipes.bin"):
    RECIPE_STRUCT = struct.Struct("i120si5500si20s4?i")
    with open(file_path, "rb") as f:
        offset = (recipe_id - 1) * RECIPE_STRUCT.size
        f.seek(offset)
        data = f.read(RECIPE_STRUCT.size)
        if not data:
            return None
        unpacked = RECIPE_STRUCT.unpack(data)
        return unpacked[4]  # tempo da receita


def parse_int(value):
    try:
        if value is None or value == "":
            return None
        return int(value)
    except:
        return None