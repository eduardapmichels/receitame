class TagNode:

    def __init__(self,tag: str):
        self.tag = tag
        self.ids=[]
        self.left = None
        self.right=None

    def add_id(self, id: int):
        self.ids.append(id)


