import re
import struct
import pickle
from pathlib import Path

from receitas.utilitario.globals import BT, TRIE
from receitas.alfabeto_index import build_alfabeto_index

# -----------------------------
# Estruturas existentes
# -----------------------------

RECIPE_STRUCT = struct.Struct("i120si5500si20s4?i")
ING_STRUCT = struct.Struct("i130s")
RECIPE_ING_STRUCT = struct.Struct("iii70s")

# -----------------------------
# Funções auxiliares
# -----------------------------

def load_ingredients_dict():
    """Carrega todos os ingredientes existentes num dicionário {nome: id}."""
    ing_file = Path("data/ingredients.bin")
    ingredients = {}

    if not ing_file.exists():
        return ingredients

    with open(ing_file, "rb") as f:
        while True:
            data = f.read(ING_STRUCT.size)
            if not data:
                break
            iid, name = ING_STRUCT.unpack(data)
            name = name.decode().strip("\x00").strip()
            if name:
                ingredients[name] = iid

    return ingredients


def next_recipe_id():
    """Calcula o próximo ID de receita baseado no tamanho de recipes.bin."""
    path = Path("data/recipes.bin")
    if not path.exists():
        return 1
    return path.stat().st_size // RECIPE_STRUCT.size + 1


def next_recipe_ingredient_id():
    """Calcula próximo ID da relação recipe_ingredient."""
    path = Path("data/recipe_ingredients.bin")
    if not path.exists():
        return 1
    return path.stat().st_size // RECIPE_ING_STRUCT.size + 1


# ------------------------------------------
# Função principal: adicionar receita nova
# ------------------------------------------

def add_new_recipe(title, instructions, time_min, difficulty, ingredients_raw):
    """
    Adiciona:
      - receita em recipes.bin
      - ingredientes novos em ingredients.bin (se necessário)
      - relações em recipe_ingredients.bin
      - atualiza BT e TRIE
    """

    # -------------------------
    # Preparar ingredientes
    # -------------------------
    ingredients_raw = [
        re.sub(r"^[^a-zA-ZÀ-ÿ]+", "", ing).strip()
        for ing in ingredients_raw
        if ing.strip()
    ]

    # carrega os ingredientes existentes
    ingredients_dict = load_ingredients_dict()
    next_ing_id = len(ingredients_dict) + 1
    next_rel_id = next_recipe_ingredient_id()

    # abrir arquivos que serão escritos
    f_ing = open("data/ingredients.bin", "ab")
    f_rel = open("data/recipe_ingredients.bin", "ab")

    # -------------------------
    # Criar receita
    # -------------------------
    rid = next_recipe_id()

    recipe_first_rel = next_rel_id if ingredients_raw else 0

    # grava a receita
    with open("data/recipes.bin", "ab") as f_recipes:
        f_recipes.write(RECIPE_STRUCT.pack(
            rid,
            title.encode(),
            1,  # subcategoria placeholder
            instructions.encode(),
            time_min,
            difficulty.encode(),
            0, 0, 0, 0,        # flags
            recipe_first_rel
        ))

    # -------------------------
    # Gravar ingredientes e relações
    # -------------------------
    for ing in ingredients_raw:
        # criar ingrediente novo se não existir
        if ing not in ingredients_dict:
            ingredients_dict[ing] = next_ing_id

            # grava ingrediente no arquivo
            f_ing.write(ING_STRUCT.pack(
                next_ing_id,
                ing.encode()[:130].ljust(130, b"\x00")
            ))

            next_ing_id += 1

        ingredient_id = ingredients_dict[ing]

        # measurement simples
        measurement = b" " * 70

        # grava relação
        f_rel.write(RECIPE_ING_STRUCT.pack(
            next_rel_id,
            rid,
            ingredient_id,
            measurement
        ))
        next_rel_id += 1

    f_ing.close()
    f_rel.close()

    # -------------------------
    # atualizar índices
    # -------------------------
    update_indexes(rid, time_min, title)

    return rid


# ------------------------------------------
# Atualiza Trie + BTree
# ------------------------------------------

def update_indexes(rid, time_min, title):
    # ---------- B+Tree ----------
    BT.insert_key(time_min, rid)
    with open("data/bptree.bin", "wb") as f:
        pickle.dump(BT, f)

    # ---------- Trie ----------
    offset = (rid - 1) * RECIPE_STRUCT.size
    TRIE.insert(title.lower(), rid, offset)
    with open("data/trie.bin", "wb") as f:
        pickle.dump(TRIE, f)