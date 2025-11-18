def __init__(self, ordem):
    if ordem < 3: ordem = 3
    if (ordem % 2 == 0): ordem += 1
    self.__m = ordem - 1
    self.__raiz = None