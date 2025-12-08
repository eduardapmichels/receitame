import struct
RECIPE_STRUCT = struct.Struct("i120s5500si20s4?i")
INGREDIENT_STRUCT = struct.Struct("i130s")
CUISINE_STRUCT = struct.Struct("i130s")
RECIPE_INGREDIENT_STRUCT = struct.Struct("iii70s")
RECIPE_CUISINE_STRUCT = struct.Struct("ii")
TAG_STRUCT = struct.Struct("130sii")
ID_STRUCT = struct.Struct("i")