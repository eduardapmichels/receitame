from .loader import load_btree_pickle, load_trie_pickle

print("Carregando BTree e Trie...")

BT = load_btree_pickle()
TRIE = load_trie_pickle()

print("Carregadas com sucesso!")