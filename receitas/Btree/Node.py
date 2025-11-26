from receitas.Btree.Key import Key
class Node:
    def __init__(self, t, is_leaf=True, parent=None):
        self.t = t
        self.max_n = 2 * t
        self.min_n = t

        self.is_leaf = is_leaf
        self.parent = parent
        
        self.nodes = []       # keys
        self.children = []    # pointers
        self.next = None      # leaf chain
        self.n = 0

    # -> binary search 
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
    
    # -> locate leaf 
    def find_leaf(self, time, recipe_id): 
        i = self.binary_search(time, recipe_id) 
        if(i==-1): 
            return None 
        if self.is_leaf: 
                return self 
        else: return self.children[i].find_leaf(time, recipe_id)


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

        # chave não existe → criar nova
        key = Key(time)
        key.recipes.append(recipe_id)
        self.nodes.insert(start, key)
        self.n += 1
        return True 


    # -> split leaf (Bayer-McCreight)
    def split_leaf(self):
        t = self.t
        mid = t 

        right = Node(t, is_leaf=True, parent=self.parent)

        right.nodes = self.nodes[mid:]
        right.n = len(right.nodes)

        self.nodes = self.nodes[:mid]
        self.n = len(self.nodes)

        right.next = self.next
        self.next = right

        promoted = right.nodes[0]  # delimiter key

        return promoted, right


    # -> split internal (Bayer-McCreight)
    def split_internal(self):
        t = self.t
        mid = t  # divide exatamente no meio

        promoted = self.nodes[mid]

        right = Node(t, is_leaf=False, parent=self.parent)

        right.nodes = self.nodes[mid+1:]
        right.children = self.children[mid+1:]
        right.n = len(right.nodes)

        for c in right.children:
            c.parent = right

        self.nodes = self.nodes[:mid]
        self.children = self.children[:mid+1]
        self.n = len(self.nodes)

        return promoted, right
