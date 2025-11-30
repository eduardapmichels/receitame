
import pickle
from pathlib import Path
from receitas.Btree.BTree import BTree
from receitas.Btree.Node import Node
from receitas.Btree.Key import Key
import struct

import math
###########################################################
#B+Tree
###########################################################
def load_btree_pickle():
    p = Path("data/bptree.bin")
    if not p.exists():
        return None
    with open(p, "rb") as f:
        bt = pickle.load(f)
    
    root = bt.get_root()
    print(root.nodes[:root.n])
    return bt

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


########################################################
# Trie - tree
#########################################################
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


###################################################################
# Arquivos invertidos
###################################################################
def load_tags(name):
    TAG_STRUCT = struct.Struct("130sii")
    index_path = Path(f"data/tags_index_{name}.bin")

    index = {}

    with open(index_path, "rb") as f:
        while True:
            chunk = f.read(TAG_STRUCT.size)
            if not chunk:
                break
            tag_bytes, count, offset = TAG_STRUCT.unpack(chunk)
            tag = tag_bytes.decode("utf-8").rstrip("\x00")
            index[tag] = (count, offset)

    return index


def load_tag_ids(name, tag, index):
    ID_STRUCT = struct.Struct("i")
    data_path = Path(f"data/tags_data_{name}.bin")

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


def build_tags_index_cache(tags_folder="data"):
    """Lê todos os arquivos de índice e retorna um cache {tag: (data_file, count, offset)}"""
    TAG_STRUCT = struct.Struct("120sii")
    
    tags_index_cache = {}
    index_files = list(Path(tags_folder).glob("tags_index_*.bin"))
    for index_path in index_files:
        data_path = Path(str(index_path).replace("index", "data"))
        with open(index_path, "rb") as f_index:
            while True:
                bytes_read = f_index.read(TAG_STRUCT.size)
                if not bytes_read:
                    break
                tag_bytes, count, offset = TAG_STRUCT.unpack(bytes_read)
                tag_name = tag_bytes.decode("utf-8").rstrip("\x00")
                tags_index_cache[tag_name] = (data_path, count, offset)
    return tags_index_cache

def intersect_tags(tags, tags_index_cache):
    """Retorna IDs que aparecem em todas as tags (modo AND)"""
    ID_STRUCT = struct.Struct("i")
    sets_of_ids = []

    for tag in tags:
        if tag not in tags_index_cache:
            # tag não existe -> interseção vazia
            return set()

        data_path, count, offset = tags_index_cache[tag]
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
    CUISINE_STRUCT = struct.Struct("i130s")
    cuisines_path = Path("data/cuisines.bin")
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
    

