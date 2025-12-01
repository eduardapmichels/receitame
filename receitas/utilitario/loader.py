from pathlib import Path
import pickle

 
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