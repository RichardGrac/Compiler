# | ------------------------------ TABLA DE SIMBOLOS --------------------------------------|
# | (variables) con su Nombre, la profundidad/número de registro, arreglo de las           |
# | lineas en donde la variable tiene una aparición, su valor (Cambiante de acuerdo a como |
# | va corriendo su compilación, el tipo de variable (boolean, int, real) y el Nodo (no es necesario)
# | ---------------------------------------------------------------------------------------|
class Symbol:
    pass

    def __init__(self, name=None, deep=None, line=[], val=None, dtype=None, node=None):
        self.name = name
        self.deep = deep
        self.lines = line
        self.val = val
        self.dtype = dtype
        self.Node = node
