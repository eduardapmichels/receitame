import struct
import json
import re
import time
from pathlib import Path


from data_handler import RECIPE_STRUCT


class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False
        self.positions = []  #lista de offsets no arquivo recipes.bin

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, position): #insere nome da receita
        node = self.root 
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.end = True
        node.positions.append(position)  #adiciona no final da lista nova posicao de offset
        
    def to_dict(self, node=None):  #transforma o TrieNode em dicionairo comum
        if node is None:
            node = self.root
        return {
            "end": node.end,
            "pos":node.positions,
            "children":{char: self.to_dict(child) for char, child in sorted(node.children.items())}
        }
    

def clean_title(title):
    return re.sub(r'[^A-Za-zÀ-ÿ ]+', '',title).lower().strip()



#funcao constroe indice
"""Abre o arquivo recipes.bin
Para cada receita:
lê o registro
pega o título
insere na TRIE com o offset
converte a TRIE para dicionário
Salva em recipes_index_alpha.json"""

def build_alfabeto_index():
    trie = Trie()
    bin_path = Path("recipes.bin")

    try:

        with open(bin_path, "rb") as f:
            offset = 0

            start = time.time()

            while True:
                data = f.read(RECIPE_STRUCT.size)
                if not data:
                    break   #ja leu arquivo

                unpacked = RECIPE_STRUCT.unpack(data) 
                recipe_title = unpacked[1].decode("utf-8").replace("\x00", "").strip()
                clean = clean_title(recipe_title)

                trie.insert(clean,offset)
                offset += RECIPE_STRUCT.size

            print("Tempo para ler + mongar trie;", time.time() - start, "segundos")

        json_start = time.time()

        index_path =  Path("data/recipes_index_alpha.json")

        with index_path.open("w", encoding="utf-8") as f:
            json.dump(trie.to_dict(), f, ensure_ascii=False)

        print("tempo para gerar json",time.time() - json_start, "segundos")

        print("Índice em ordem alfabetica criado com sucesso")
    except FileNotFoundError:
        print(f"ERRO: ARQUIVO NAO ENCONTRADO EM {bin_path}. VERIFIQUE O CAMINHP")
    except Exception as e:
        print(f"ERRO dirante a construcao do indic: {e}")


if __name__ =="__main__":
    build_alfabeto_index()



"""
import struct
import json
import re
from pathlib import Path
import time


from data_handler import RECIPE_STRUCT


class TrieNode:
    def __init__(self):
        self.children = {}   # agora guarda prefixos, não caracteres individuais
        self.end = False
        self.positions = []


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, position):
        node = self.root

        while word:
            #procura prefixos existentes
            for prefix in list(node.children.keys()):
                common = self._common_prefix(word, prefix)

                if common == "":
                    continue

                #caso 1: prefixo igual ao prefixo da aresta → desce
                if common == prefix:
                    word = word[len(prefix):]
                    node = node.children[prefix]
                    break

                #caso 2: prefixo parcial - split da aresta
                if common != prefix:
                    old_child = node.children[prefix]
                    new_child = TrieNode()

                    #parte restante antiga
                    suffix_old = prefix[len(common):]
                    new_child.children[suffix_old] = old_child

                    #novo nó substitui prefixo antigo
                    node.children.pop(prefix)
                    node.children[common] = new_child

                    node = new_child
                    word = word[len(common):]
                    break
            else:
                #nenhum prefixo combina - cria nova aresta com o resto da palavra
                new_node = TrieNode()
                node.children[word] = new_node
                node = new_node
                word = ""
        
        node.end = True
        node.positions.append(position)

    def _common_prefix(self, a, b):
        size = min(len(a), len(b))
        i = 0
        while i < size and a[i] == b[i]:
            i += 1
        return a[:i]

    def to_dict(self, node=None):
        if node is None:
            node = self.root

        return {
            "end": node.end,
            "pos": node.positions,
            "children": {
                key: self.to_dict(child)
                for key, child in sorted(node.children.items())
            }
        }


def clean_title(title):
    return re.sub(r'[^A-Za-zÀ-ÿ ]+', '', title).lower().strip()


def build_alfabeto_index():
    trie = Trie()
    bin_path = Path("recipes.bin")

    try:
        with open(bin_path, "rb") as f:
            offset = 0

            start = time.time()

            while True:
                data = f.read(RECIPE_STRUCT.size)
                if not data:
                    break

                unpacked = RECIPE_STRUCT.unpack(data)
                recipe_title = unpacked[1].decode("utf-8").replace("\x00", "").strip()
                clean = clean_title(recipe_title)

                trie.insert(clean, offset)
                offset += RECIPE_STRUCT.size
            
            print("Tempo para ler + mongar trie;", time.time() - start, "segundos")

        json_start = time.time()

        index_path = Path("data/recipes_index_alpha.json")

        with index_path.open("w", encoding="utf-8") as f:
            json.dump(trie.to_dict(), f, ensure_ascii=False)

        print("tempo para gerar json",time.time() - json_start, "segundos")

        print("Índice em ordem alfabetica criado com sucesso (PATRICIA TRIE)")

    except FileNotFoundError:
        print(f"ERRO: ARQUIVO NAO ENCONTRADO EM {bin_path}. VERIFIQUE O CAMINHO")
    except Exception as e:
        print(f"ERRO durante a construçao do índice: {e}")


if __name__ == "__main__":
    build_alfabeto_index()"""