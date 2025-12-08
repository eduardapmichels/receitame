from .loader import load_btree_pickle, load_trie_pickle, load_tags
from receitas.Btree.BTree import BTree
from receitas.alfabeto_index import Trie
from pathlib import Path

print("Carregando BTree, Trie e índices de Arquivos invertidos (init lazy)...")

# inicialmente tenta carregar (como você já fazia)
BT = load_btree_pickle()
TRIE = load_trie_pickle()
TAGS = {
    **load_tags("flags"),
    **load_tags("cuisines"),
    **load_tags("difficulty")
}

def ensure_indexes_loaded():
    """
    Garante que BT e TRIE não fiquem None. 
    Chamadas idempotentes — seguras para chamar várias vezes.
    """
    global BT, TRIE, TAGS

    if BT is None:
        print("[globals] BT is None -> criando BTree vazia e (re)tentando construir index")
        # cria uma BTree vazia para não quebrar — dependendo do caso, você pode preferir
        # reconstruir o índice chamando sua rotina de build (mas isso é custoso).
        BT = BTree(50)
        # tenta carregar novamente do disco:
        bt_loaded = load_btree_pickle()
        if bt_loaded is not None:
            BT = bt_loaded

    if TRIE is None:
        print("[globals] TRIE is None -> criando Trie vazia e tentando recarregar do disco")
        TRIE = Trie()  # instância vazia para não quebrar chamadas
        trie_loaded = load_trie_pickle()
        if trie_loaded is not None:
            TRIE = trie_loaded

    if not TAGS:
        print("[globals] TAGS vazio -> tentando recarregar tags")
        TAGS = {
            **load_tags("flags"),
            **load_tags("cuisines"),
            **load_tags("difficulty")
        }

    # prints breves para debugging em ambiente de dev
    print(f"[globals] BT={'OK' if BT is not None else 'None'}, TRIE={'OK' if TRIE is not None else 'None'}, TAGS_count={len(TAGS)}")
