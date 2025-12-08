import struct
import re
import time
import pickle
from pathlib import Path
from receitas.structs import *


class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False
        self.positions = []  #lista de offsets no arquivo recipes.bin

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word,recipe_id, position): #insere nome da receita
        node = self.root 
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.end = True
        node.positions.append((recipe_id,position))  #adiciona no final da lista nova posicao de offset
        
    def to_dict(self, node=None):  #transforma o TrieNode em dicionairo comum
        if node is None:
            node = self.root
        return {
            "end": node.end,
            "pos":node.positions,
            "children":{char: self.to_dict(child) for char, child in sorted(node.children.items())}
        }
    


#funcao constroe indice
"""Abre o arquivo recipes.bin
Para cada receita:
lê o registro
pega o título
insere na TRIE com o offset
converte a TRIE para dicionário
Salva em recipes_index.bin"""

def build_alfabeto_index(trie: Trie):
    bin_path = Path("receitas/data/recipes.bin")
   

    try:

        with open(bin_path, "rb") as f:
            print(f)
            offset = 0
            start = time.time()
            while True:
                data = f.read(RECIPE_STRUCT.size)
                if not data:
                    break   #ja leu arquivo
                

                unpacked = RECIPE_STRUCT.unpack(data) 
                recipe_id = unpacked[0]
                recipe_title = unpacked[1].decode("utf-8").replace("\x00", "").strip()

                trie.insert(recipe_title,recipe_id,offset)
                offset += RECIPE_STRUCT.size

            print("Tempo para ler + mongar trie;", time.time() - start, "segundos")

        bin_start = time.time()

        index_path =  Path("receitas/data/trie.bin")

        with index_path.open("wb") as f:
            pickle.dump(trie, f)

        print("tempo para gerar bin",time.time() - bin_start, "segundos")

        print("Índice em ordem alfabetica criado com sucesso")
        return trie
    except FileNotFoundError:
        print(f"ERRO: ARQUIVO NAO ENCONTRADO EM {bin_path}. VERIFIQUE O CAMINHP")
    except Exception as e:
        print(f"ERRO dirante a construcao do indic: {e}")



if __name__ =="__main__":
    build_alfabeto_index()

