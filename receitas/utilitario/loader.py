from pathlib import Path
import pickle
from receitas.structs import *


def load_btree_pickle():
    p = Path("receitas/data/bptree.bin")
    print(f"[loader] load_btree_pickle: tentando {p}")
    if not p.exists():
        print(f"[loader] bptree.bin não encontrado em {p}")
        return None
    try:
        with open(p, "rb") as f:
            bt = pickle.load(f)
        # debug simples — pode falhar se bt não tiver get_root
        try:
            root = bt.get_root()
            print("[loader] bptree carregado. root preview:", getattr(root, "nodes", None))
        except Exception as e:
            print("[loader] bptree carregado mas não foi possível inspecionar root:", e)
        return bt
    except Exception as e:
        print("[loader] Erro ao desserializar bptree.bin:", e)
        return None

def load_trie_pickle():
    p = Path("receitas/data/trie.bin")
    print(f"[loader] load_trie_pickle: tentando {p}")
    if not p.exists():
        print(f"[loader] trie.bin não encontrado em {p}")
        return None
    try:
        with open(p, "rb") as f:
            trie = pickle.load(f)
        # sanity check
        if hasattr(trie, "root"):
            print("[loader] trie carregado com sucesso. root ok.")
        else:
            print("[loader] trie carregado mas não tem atributo 'root'.")
        return trie
    except Exception as e:
        print("[loader] Erro ao desserializar trie.bin:", e)
        return None

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
