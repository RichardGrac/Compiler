from enum import Enum

class Token:
    pass
    columna = 0
    linea = 0
    tipo = ""
    lexema = ""

    def __init__(self, linea, columna, tipo, lexema):
        self.columna = columna
        self.linea = linea
        self.tipo = tipo
        self.lexema = lexema


class NodeKind(Enum):
    StmtK = 1
    ExpK = 2


class StmtKind(Enum):
    MainK = 1
    IfK = 2
    CoutK = 3
    CinK = 4
    DeclK = 5
    AssignK = 6
    RepeatK = 7
    UntilK = 8
    WhileK = 9
    ThenK = 10
    ElseK = 11


class ExpKind(Enum):
    OpK = 1
    ConstK = 2
    IdK = 3


class ExpType:
    def __init__(self):
        self.Real = 0.0
        self.Integer = 0
        self.Boolean = False


class Kind(Enum):
    stmt = StmtKind  # StmtKind = Objeto que contiene el tipo de Statement
    exp = ExpKind  # ExpKind = Objecto que contiene el tipo de Expresión


class Attr:
    def __init__(self):
        self.tipe = ""
        self.val = 0.0
        self.name = ""


class TreeNode:
    pass

    def __init__(self):
        self.token = Token(None, None, None, None)  # Token
        self.sibling = []  # Hermanos
        self.nodeKind = None  # Exp o Stmt
        self.kind = None  # Kind
        self.attr = Attr()  # Atributos
        self.expType = None  # Real,Int,Boolean
        self.branch = [None] * 3  # Hijos