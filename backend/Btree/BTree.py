import Node

class BTree:
    '''B+ Tree using Bayer-McCreight properties'''
    def __init__(self, t: int):
        self.t = t
        self.max_keys = t*2   #max number of keys in a node
        self.raiz = None

