import pickle
from pathlib import Path
from receitas.alfabeto_index import build_alfabeto_index
from receitas.utilitario.globals import TRIE

def rebuild_trie():
    """Reconstrói a TRIE a partir do recipes.bin"""
    build_alfabeto_index(TRIE)
    print("TRIE reconstruída com sucesso ao iniciar o servidor")