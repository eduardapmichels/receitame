from .loader import load_btree_pickle, load_trie_pickle, load_tags
from receitas.Btree.BTree import BTree
from receitas.alfabeto_index import Trie
from pathlib import Path

#debug
print("Carregando BTree, Trie e índices de Arquivos invertidos (init lazy)...")

# carrega se nao existir retorna none
BT = load_btree_pickle()
TRIE = load_trie_pickle()
TAGS = {
    **load_tags("flags"),
    **load_tags("cuisines"),
    **load_tags("difficulty")
}


#chamada quando view precisa acessar trie, btree ou tags
def ensure_indexes_loaded():
    global BT, TRIE, TAGS

    if BT is None:
        print("[globals] BT is None -> criando BTree vazia e (re)tentando construir index")
        # cria uma BTree vazia para não quebrar
        #tenta carregar se conseguir, substirui. Se nao conseguir, usa a vazia para nao quebrar
        BT = BTree(50)
        bt_loaded = load_btree_pickle()
        if bt_loaded is not None:
            BT = bt_loaded

    if TRIE is None:
        #cria trie vazia, tenta carregar e isa a que conseguir carregar
        TRIE = Trie()  # instância vazia para não quebrar chamadas
        trie_loaded = load_trie_pickle()
        if trie_loaded is not None:
            TRIE = trie_loaded

    #se dicionario vazio, tenta recarregar
    if not TAGS:
        print("[globals] TAGS vazio -> tentando recarregar tags")
        TAGS = {
            **load_tags("flags"),
            **load_tags("cuisines"),
            **load_tags("difficulty")
        }

    # prints breves para debugging em ambiente de dev
    print(f"[globals] BT={'OK' if BT is not None else 'None'}, TRIE={'OK' if TRIE is not None else 'None'}, TAGS_count={len(TAGS)}")
