from receitas.Btree.Key import Key

#t = grau min b+tree
#max_n = 2t max de chaves
#min_n = t min chaves (exceto raiz)
class Node:
    def __init__(self, t, is_leaf=True, parent=None):
        self.t = t
        self.max_n = 2 * t
        self.min_n = t

        self.is_leaf = is_leaf
        self.parent = parent
        #nodes = lista de key
        self.nodes = []    
        #ponteiros para os nos filhos (so internos)
        self.children = []    
        #ponteiro para a prox folha
        self.next = None  
        #numero de chaves no nó   
        self.n = 0

    #busca binaria
    #se encontra uma chave com o mesmo time, adiciona o recipe_id na lista de recipes e retorna -1 indicando que nao deve continuar a insercao. senao retorna a posicao correta onde deve ser inserido
    def binary_search(self, time, recipe_id): 
        start, end = 0, self.n 
        while start < end: 
            mid = (start + end) // 2 
            if self.nodes[mid].time < time: 
                start = mid + 1 
            elif self.nodes[mid].time == time: 
                self.nodes[mid].recipes.append(recipe_id) 
                return -1 
            else: end = mid 
            return start 
    
    #busca a posicao que teria essa chave em um nó, se a chave ja existe, nada a inserir - retorna none-,se o no é folha retorna ele, caso contrario segue recursivamente ate o filho certo
    def find_leaf(self, time, recipe_id): 
        i = self.binary_search(time, recipe_id) 
        if(i==-1): 
            return None 
        if self.is_leaf: 
                return self 
        else: return self.children[i].find_leaf(time, recipe_id)


    #executa busca binaria para achar posicao, se ja existe chave com esse time, so adiciona o ID, nao duplica keys
    #se é chave nova: cria key(time), adiciona recipe_id, insere ordenado e incrementa n
    def insert_in_leaf(self, time: int, recipe_id):
        # procura a posição
        start, end = 0, self.n
        while start < end:
            mid = (start + end) // 2
            if self.nodes[mid].time < time:
                start = mid + 1
            elif self.nodes[mid].time == time:
                self.nodes[mid].recipes.append(recipe_id)
                return False  # não precisa inserir
            else:
                end = mid

        #chave não existe, criar nova
        key = Key(time)
        key.recipes.append(recipe_id)
        self.nodes.insert(start, key)
        self.n += 1
        return True 


    def split_leaf(self):
        t = self.t
        mid = t 
        #cria novo no (irmao direito)
        right = Node(t, is_leaf=True, parent=self.parent)

        #divide metade das chaves, no atual fica com primeira metade das chaves e o novo no recebe a segunda metade 
        right.nodes = self.nodes[mid:]
        right.n = len(right.nodes)

        self.nodes = self.nodes[:mid]
        self.n = len(self.nodes)

        #atualiza encadeamente de folhas, garante folhas fiquem em ordem
        right.next = self.next
        self.next = right

        #primeira chave do novo no, delimita key
        promoted = right.nodes[0]  

        return promoted, right


    #divsao no interno
    def split_internal(self):
        t = self.t
        mid = t  #divide exatamente no meio

        promoted = self.nodes[mid]

        #cria no direito
        right = Node(t, is_leaf=False, parent=self.parent)

        #divide chaves e filhos
        right.nodes = self.nodes[mid+1:]
        right.children = self.children[mid+1:]
        right.n = len(right.nodes)

        #ajusta ponteiros filhos
        for c in right.children:
            c.parent = right

        #atualiza no atual (esquerdo)
        self.nodes = self.nodes[:mid]
        self.children = self.children[:mid+1]
        self.n = len(self.nodes)

        #retorna chave promovida e novo nó
        return promoted, right
