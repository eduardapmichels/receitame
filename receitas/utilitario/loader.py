from pathlib import Path
import pickle
from receitas.structs import *

#define caminho arquivo e imprime no terminal
def load_btree_pickle():
    p = Path("receitas/data/bptree.bin")
    print(f"[loader] load_btree_pickle: tentando {p}")
    #se nao existe retorna none
    if not p.exists():
        print(f"[loader] bptree.bin não encontrado em {p}")
        return None
    try:
        #abre o arqivo binario e desserializa 
        with open(p, "rb") as f:
            bt = pickle.load(f)
        # debug simples — pode falhar se bt não tiver get_root
        try:
            #tenta chamar get_root para ver se btree esta certa
            root = bt.get_root()
            print("[loader] bptree carregado. root preview:", getattr(root, "nodes", None))
            #caso falhe avisa
        except Exception as e:
            print("[loader] bptree carregado mas não foi possível inspecionar root:", e)
        return bt
    #se erro geral retorna none
    except Exception as e:
        print("[loader] Erro ao desserializar bptree.bin:", e)
        return None

def load_trie_pickle():
    #cria caminho
    p = Path("receitas/data/trie.bin")
    print(f"[loader] load_trie_pickle: tentando {p}")
    #se nao existe printa
    if not p.exists():
        print(f"[loader] trie.bin não encontrado em {p}")
        return None
    try:
        #carrega
        with open(p, "rb") as f:
            trie = pickle.load(f)
        #garante trie carrege inteira
        if hasattr(trie, "root"):
            print("[loader] trie carregado com sucesso. root ok.")
        else:
            print("[loader] trie carregado mas não tem atributo 'root'.")
        return trie
    #caso erro
    except Exception as e:
        print("[loader] Erro ao desserializar trie.bin:", e)
        return None

def load_tags(name):
    index_path = Path(f"receitas/data/tags_index_{name}.bin")
    data_path = Path(f"receitas/data/tags_data_{name}.bin")

    #dicionario final
    index = {}
    #se indice nao existe sem tags
    if not index_path.exists():
        return {}

    #le arquivo, tag_bytes = nome da tag (em bytes), count (quantos elementos existem), offset (onde esta a lista dentro do arquivo)
    with open(index_path, "rb") as f:
        while True:
            chunk = f.read(TAG_STRUCT.size)
            if not chunk:
                break
            tag_bytes, count, offset = TAG_STRUCT.unpack(chunk)
            #converte tag para string e remove zeros no final
            tag = tag_bytes.decode("utf-8").rstrip("\x00")
            #salva dicionario
            index[tag] = (str(data_path), count, offset)

            #tag mapeada com caminho, quant de itens e offset, o necessario para localizar as receitas

    return index
