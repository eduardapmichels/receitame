class Node:
    '''A class representing a node in a b+ tree structure.'''
    def __init__(self, t):
        self.n = 0          #number of keys the node has
        self.parent=None
        self.is_leaf = False
        self.next = None
        self.max_n=2*t
        self.nodes = [] * (self.max_n)
        self.children = None
        

    #getters
    def get_time(self):
        return self.time
    
    def get_left(self):
        return self.left
    
    def get_right(self):
        return self.right
    
    def get_recipes(self):
        return self.recipes

    #setters

    def set_left(self, No):
        self.left = No

    def set_right(self, No):
        self.right = No

