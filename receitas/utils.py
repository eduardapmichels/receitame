
import pickle
from pathlib import Path
from receitas.Btree.BTree import BTree
from receitas.Btree.Node import Node
from receitas.Btree.Key import Key
import struct

def load_btree_pickle():
    p = Path("data/bptree.bin")
    if not p.exists():
        return None
    with open(p, "rb") as f:
        bt = pickle.load(f)
    
    root = bt.get_root()
    print(root.nodes[:root.n])
    return bt


import math
def get_recipes_page(bt, page=1, per_page=200, min_time=None, max_time=None):
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
                all_filtered.append((key.time, recipe_id))

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
    for time, recipe_id in page_items:
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
    

def parse_int(value):
    try:
        if value is None or value == "":
            return None
        return int(value)
    except:
        return None