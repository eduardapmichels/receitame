from pathlib import Path
import pickle
from receitas.structs import *
 
def load_btree_pickle():
    p = Path("receitas/data/bptree.bin")
    if not p.exists():
        return None
    with open(p, "rb") as f:
        bt = pickle.load(f)
    
    root = bt.get_root()
    print(root.nodes[:root.n])
    return bt


def load_trie_pickle():
    p = Path("receitas/data/trie.bin")
    if not p.exists():
        return None
    with open(p, "rb") as f:
        trie = pickle.load(f)
    return trie

def load_tags(name):
    index_path = Path(f"receitas/data/tags_index_{name}.bin")
    data_path = Path(f"receitas/data/tags_data_{name}.bin")

    index = {}

    if not index_path.exists():
        return {}

    with open(index_path, "rb") as f:
        while True:
            chunk = f.read(TAG_STRUCT.size)
            if not chunk:
                break
            tag_bytes, count, offset = TAG_STRUCT.unpack(chunk)
            tag = tag_bytes.decode("utf-8").rstrip("\x00")
            index[tag] = (str(data_path), count, offset)

    return index
