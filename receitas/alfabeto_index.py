import struct
import re
import time
import pickle
from pathlib import Path
from receitas.structs import *

#children = dicionario, cada no representa uma letra e aponta para os prox nos 
#end = fim da palavra b->o->l->o-> (end=true)
#positions serve para achar rapidos as receitas cujo titulo corresponde a palavra que termina nesse no 
class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False
        self.positions = []  #lista de offsets no arquivo recipes.bin

#raiz da trie
class Trie:
    def __init__(self):
        self.root = TrieNode()

#comeca na raiz, percorre cada caractere do titulo, cria um novo no se nao existir, avanca e no fim da palavra grava end=true e salva o recipe_id, posicao_no_arquivo para busca dps
    def insert(self, word,recipe_id, position): #insere nome da receita
        node = self.root 
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.end = True
        node.positions.append((recipe_id,position))  #adiciona no final da lista nova posicao de offset


#converte trie para dicionario (usado para debuggar estrututa, visualizar mais facilmente, nos tinhamos salvado em json antes para ver se estava certo) 
    def to_dict(self, node=None):  #transforma o TrieNode em dicionairo comum
        if node is None:
            node = self.root
        return {
            "end": node.end,
            "pos":node.positions,
            "children":{char: self.to_dict(child) for char, child in sorted(node.children.items())}
        }
    



#cria o indice alfabetico

#le arquivo recipes.bin
#pega cada titulo
#insere na trie junto com id e offset
#salva trie em trie.bin
def build_alfabeto_index(trie: Trie):
    bin_path = Path("receitas/data/recipes.bin")
   

    try:
        #le binario
        with open(bin_path, "rb") as f:
            print(f)
            #offset inicio cada um tem o tamanho fixo RECIPE_STRUCT.size
            offset = 0
            start = time.time()
            #le um registro por vez
            while True:
                data = f.read(RECIPE_STRUCT.size)
                if not data:
                    break   #ja leu arquivo
                
                #pega a receita, tranforma bytes em campos no python recipe_title é a titulo limpo sem zeros
                unpacked = RECIPE_STRUCT.unpack(data) 
                recipe_id = unpacked[0]
                recipe_title = unpacked[1].decode("utf-8").replace("\x00", "").strip()

                #insere tirulo na trie, cada titulo vira um caminho na trie
                trie.insert(recipe_title,recipe_id,offset)
                offset += RECIPE_STRUCT.size

            print("Tempo para ler + mongar trie;", time.time() - start, "segundos")

        bin_start = time.time()

        index_path =  Path("receitas/data/trie.bin")
        #serializa a trie
        with index_path.open("wb") as f:
            pickle.dump(trie, f)

        print("tempo para gerar bin",time.time() - bin_start, "segundos")

        print("Índice em ordem alfabetica criado com sucesso")
        return trie
    #controle de erro
    except FileNotFoundError:
        print(f"ERRO: ARQUIVO NAO ENCONTRADO EM {bin_path}. VERIFIQUE O CAMINHP")
    except Exception as e:
        print(f"ERRO dirante a construcao do indic: {e}")


#chama funcao
if __name__ =="__main__":
    build_alfabeto_index()