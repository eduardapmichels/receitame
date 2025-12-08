from pathlib import Path
import struct
from receitas.structs import *

from receitas.invertedIndex.tagnode import TagNode


class BinarySearchTree:
    def __init__(self):
        self.root=None

    def binary_search(self, tag:str, current_node:TagNode):
        if(tag==current_node.tag):
            return current_node
        elif(tag<current_node.tag):
            if current_node.left!=None:
                current_node=self.binary_search(tag, current_node.left)
            else:
                auxiliar=current_node
                current_node = TagNode(tag)
                auxiliar.left=current_node

        else:
            if current_node.right!=None:
                current_node=self.binary_search(tag, current_node.right)
            else:
                auxiliar=current_node
                current_node = TagNode(tag)
                auxiliar.right=current_node      
        return current_node
    
    def insert_recipe(self,tag:str, id:int):

        if(self.root==None):
            node=TagNode(tag)
            node.add_id(id)
            self.root = node

        else:
            node = self.binary_search(tag, self.root)
            node.add_id(id)

    def print_left_center(self, node: TagNode):
        if(node.left!=None):
            self.print_left_center(node.left)
        print(node.tag)
        if(node.right!=None):
            self.print_left_center(node.right)


    def to_inverted_file(self, name):



        tags_data = Path(f"receitas/data/tags_data_{name}.bin")
        tags_index = Path(f"receitas/data/tags_index_{name}.bin")

        with open(tags_data, "wb") as td, open(tags_index, "wb") as ti:

            def write_file(node, offset):
                if node is None:
                    return offset
                # esquerda
                offset = write_file(node.left, offset)
                # salva posição inicial dos IDs deste node
                start_offset = offset
                # escreve todos os IDs
                for rid in node.ids:
                    td.write(ID_STRUCT.pack(rid))
                    offset += 4   # avançamos 4 bytes por ID (struct "i")
                # escreve indexagem da tag
                tag_bytes = node.tag.encode("utf-8")
                tag_bytes = tag_bytes.ljust(130, b'\x00')
                ti.write(
                    TAG_STRUCT.pack(
                        tag_bytes,
                        len(node.ids),
                        start_offset
                    )
                )
                # direita
                offset = write_file(node.right, offset)
                return offset
            # inicia com offset = 0
            write_file(self.root, 0)
    
