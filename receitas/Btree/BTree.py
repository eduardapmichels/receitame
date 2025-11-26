from receitas.Btree.Node import Node

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
