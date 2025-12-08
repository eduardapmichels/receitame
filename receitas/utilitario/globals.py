from .loader import load_btree_pickle, load_trie_pickle, load_tags

print("Carregando BTree, Trie e índices de Arquivos invertidos...")

BT = load_btree_pickle()
TRIE = load_trie_pickle()
TAGS = {
    **load_tags("flags"),
    **load_tags("cuisines"),
    **load_tags("difficulty")
}
print("Carregadas com sucesso!")