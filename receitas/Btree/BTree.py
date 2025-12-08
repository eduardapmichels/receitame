from receitas.Btree.Node import Node
from pathlib import Path
import pickle
import time
from receitas.structs import *

class BTree:
    def __init__(self, t):
        self.t = t
        self.root = Node(t, is_leaf=True)


    def get_root(self):
        return self.root

    def insert_key(self, time: int, recipe_id):
        leaf = self.root.find_leaf(time, recipe_id)
        if leaf is not None:
            inserted = leaf.insert_in_leaf(time, recipe_id)
            if inserted and leaf.n > leaf.max_n:
                self.handle_split(leaf)

    def handle_split(self, node: Node):
        if node.is_leaf:
            promoted, right = node.split_leaf()
        else:
            promoted, right = node.split_internal()

        if node.parent is None:
            new_root = Node(self.t, is_leaf=False)
            new_root.nodes = [promoted]
            new_root.children = [node, right]
            node.parent = new_root
            right.parent = new_root
            new_root.n = 1
            self.root = new_root
            return

        parent = node.parent
        if type(parent)==Node:
            pos = parent.binary_search(promoted.time, -1)
            parent.nodes.insert(pos, promoted)
            parent.children.insert(pos+1, right)
            parent.n += 1
            right.parent = parent

            if parent.n > parent.max_n:
                self.handle_split(parent)
    

    def print_tree(self, node, prefix="", is_last=True):
        """Imprime a árvore em formato de diretórios, incluindo ponteiro next nas folhas."""
    
        connector = "└── " if is_last else "├── "

        # Mostrar chaves do nó
        if node.is_leaf:
            print(prefix + connector + f"Leaf { [k.time for k in node.nodes] }")
        else:
            print(prefix + connector + f"Internal { [k.time for k in node.nodes] }")

        # Preparar prefixo para filhos
        if not node.is_leaf:
            new_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(node.children):
                self.print_tree(child, new_prefix, i == len(node.children) - 1)

    
        
def build_bptree_index(bpt: BTree):
    bin_path = Path("receitas/data/recipes.bin")


    try:
        with open(bin_path, "rb") as f:
            start = time.time()
            while True:
                data = f.read(RECIPE_STRUCT.size)
                if not data:
                    break   #ja leu arquivo
                

                unpacked = RECIPE_STRUCT.unpack(data) 
                recipe_id = unpacked[0]
                recipe_time = unpacked[3]

                bpt.insert_key(recipe_time, recipe_id)

            print("Tempo para ler + mongar b+tree;", time.time() - start, "segundos")

        bin_start = time.time()

        index_path =  Path("receitas/data/bptree.bin")

        with index_path.open("wb") as f:
            pickle.dump(bpt, f)

        print("tempo para gerar bin",time.time() - bin_start, "segundos")

        print("Índice em ordem de tempo criado com sucesso")
        return bpt
    except FileNotFoundError:
        print(f"ERRO: ARQUIVO NAO ENCONTRADO EM {bin_path}. VERIFIQUE O CAMINHP")
    except Exception as e:
        print(f"ERRO dirante a construcao do indic: {e}")

