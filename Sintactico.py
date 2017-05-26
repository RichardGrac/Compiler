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
    DoK = 7
    UntilK = 8
    WhileK = 9


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
    stmt = None  # StmtKind
    exp = None  # ExpKind


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


# ------------------------------------- INICIO DE ANALIZADOR SINTÁCTICO -----------------------------

tokens = []  # Todos los tokens salidos del Léxico
token = None  # Token actual
contador = 0  # Para recorrer los tokens

output = open("Tokens.txt", "r")
for line in output:
    linea, columna, tipo, lexema = line.split(" ")
    tok = Token(linea, columna, tipo, lexema[:-1])  # Substring hasta -1 porque agregaba "\n"
    tokens.append(tok)


def match(expected):
    pass
    global token
    if expected == token.tipo:
        token = getToken()
    else:
        print("Syntax error, unexpected '" + token.lexema + "' was expected: " + expected +
              " on line " + token.linea)
        output.write("Syntax error, unexpected '" + token.lexema + "' was expected: " + expected +
                     " on line " + token.linea + "\n")


def getToken():
    pass
    global contador, tokens
    if contador < len(tokens):
        tok = tokens[contador]
        contador += 1
        return tok
    else:
        return "EOF"  # End of file


def newStmtNode(kind):
    pass
    global token
    t = TreeNode()
    t.token = token

    i = 0
    while i < 3:
        t.nodeKind = NodeKind.StmtK
        t.kind = Kind.stmt
        i += 1
    return t


def newExpNode(ExpKind):
    pass
    global token
    t = TreeNode()
    t.token = token

    i = 0
    while i < 3:
        t.nodeKind = NodeKind.ExpK
        t.kind = Kind.exp
        i += 1
    return t


def stmt_sequence():
    pass
    global token
    t = statement()
    p = t

    if token == "EOF":
        try:
            match("TKN_RBRACE")
        except:
            pass
        return t

    while token.tipo != "TKN_RBRACE":
        q = statement()

        if q is not None:
            if t is None:
                p = q
                t = p
            else:
                p.sibling.append(q)
                p = q
    try:
        match("TKN_RBRACE")
    except:
        pass
    return t


def statement():
    pass
    global token

    t = TreeNode()
    if token.tipo == "TKN_ID":
        t = assign_stmt()
        match("TKN_SEMICOLON")

    elif token.tipo == "TKN_IF":
        t = if_stmt()

    elif token.tipo == "TKN_CIN":
        t = cin_stmt()
        match("TKN_SEMICOLON")

    elif token.tipo == "TKN_COUT":
        t = cout_stmt()
        match("TKN_SEMICOLON")

    elif (token.tipo == "TKN_REAL") | (token.tipo == "TKN_INT") | (token.tipo == "TKN_BOOLEAN"):
        t = declaration_stmt()
        match("TKN_SEMICOLON")

    elif token.tipo == "TKN_RBRACE":
        pass

    elif token.tipo == "TKN_WHILE":
        t = while_stmt()

    elif token.tipo == "TKN_DO":
        t = do_stmt()
        match("TKN_SEMICOLON")

    elif token.tipo == "TKN_MAIN":
        t = main_stmt()

    else:  # Caso default
        print("Syntax error, unexpected statement '" + token.lexema + "'" + " on line " + token.linea)
        output.write("Syntax error, unexpected statement '" + token.lexema + "'" + " on line " + token.linea + "\n")
        token = getToken()
    return t


def main_stmt():
    global token
    t = newStmtNode(StmtKind.MainK)
    match("TKN_MAIN")
    match("TKN_LBRACE")

    if t is not None:
        t.branch[0] = stmt_sequence()
    return t


def if_stmt():
    global token
    t = newStmtNode(StmtKind.IfK)
    match("TKN_IF")

    if t is not None:
        match("TKN_LPAREN")
        t.branch[0] = expresion()
        match("TKN_RPAREN")

    match("TKN_THEN")
    match("TKN_LBRACE")

    if t is not None:
        t.branch[1] = stmt_sequence()

    if token.lexema == "else":
        match("TKN_ELSE")
        match("TKN_LBRACE")

        if t is not None:
            t.branch[2] = stmt_sequence()

    # match("TKN_FI")

    if token.tipo == "TKN_RBRACE":
        pass
    else:
        t.sibling.append(statement())
    return t


def while_stmt():
    t = newStmtNode(StmtKind.WhileK)
    match("TKN_WHILE")

    if t is not None:
        match("TKN_LPAREN")
        t.branch[0] = expresion()
        match("TKN_RPAREN")

    match("TKN_LBRACE")

    if t is not None:
        t.branch[1] = stmt_sequence()
    return t


def do_stmt():
    t = newStmtNode(StmtKind.DoK)
    match("TKN_DO")
    match("TKN_LBRACE")

    if t is not None:
        t.branch[0] = stmt_sequence()

    match("TKN_UNTIL")

    if t is not None:
        match("TKN_LPAREN")
        t.branch[1] = expresion()
        match("TKN_RPAREN")
    return t


def declaration_stmt():
    t = newStmtNode(StmtKind.DeclK)
    TKN_TIPO = ""

    if token.lexema == "real":
        TKN_TIPO = "TKN_REAL"
    elif token.lexema == "boolean":
        TKN_TIPO = "TKN_BOOLEAN"
    elif token.lexema == "int":
        TKN_TIPO = "TKN_INT"

    match(TKN_TIPO)
    w = newStmtNode(StmtKind.AssignK)
    t.branch[0] = w
    flag = False

    while True:  # Posterior a la Declaracion debe seguirle un ID por lo menos
        q = None
        p = newStmtNode(StmtKind.AssignK)

        i = 0
        e = t.branch[0]
        while e is not None:
            q = e
            try:
                e = e.sibling[i]
            except:
                e = None
            i += 1

        if token.tipo == "TKN_ID":
            q.attr.name = token.lexema
            q.attr.tipe = token.lexema
            if flag:
                q.sibling.append(p)
        else:
            print("Syntax error, unexpected declaration_stmt '" + token.lexema + "'" + " on line " + token.linea)
            output.write("Syntax error, unexpected declaration_stmt '" + token.lexema + "'" + " on line " +
                         token.linea + "\n")

        match("TKN_ID")

        if (token.tipo == "TKN_COMMA") | (token.tipo == "TKN_ID"):  # Es error si pone dos o más ID's sin coma
            match("TKN_COMMA")

        flag = True

        if token.tipo != "TKN_ID":  # Si ya no hay otro ID, rompemos.
            break
    return t


def assign_stmt():
    global token
    q = newStmtNode(StmtKind.AssignK)

    if (q is not None) & (token.tipo == "TKN_ID"):
        q.attr.name = token.lexema

    match("TKN_ID")
    t = newStmtNode(StmtKind.AssignK)

    if (t is not None) & (token.tipo == "TKN_ASSIGN"):
        t.attr.name = token

    match("TKN_ASSIGN")

    if t is not None:
        t.branch[0] = q
        t.branch[1] = expresion()
    return t


def cin_stmt():
    global token
    t = newStmtNode(StmtKind.CinK)
    match("TKN_CIN")

    if (t is not None) & (token.tipo == "TKN_ID"):
        t.attr.name = token.lexema
        t.branch[0] = newExpNode(ExpKind.IdK)

    match("TKN_ID")
    return t


def cout_stmt():
    pass
    global token
    t = newStmtNode(StmtKind.CoutK)
    match("TKN_COUT")

    if t is not None:
        t.branch[0] = expresion()
    return t


def isLogic():
    pass
    global token
    if (token.tipo == "TKN_LESS") | (token.tipo == "TKN_ELESS"):
        return True
    elif (token.tipo == "TKN_EQUAL") | (token.tipo == "TKN_NEQUAL"):
        return True
    elif (token.tipo == "TKN_MORE") | (token.tipo == "TKN_EMORE"):
        return True
    else:
        return False


def expresion():
    pass
    global token
    t = exp()

    while (token.tipo == "TKN_AND") | (token.tipo == "TKN_OR"):
        p = newExpNode(ExpKind.OpK)

        if p is not None:
            p.branch[0] = t
            p.attr.op = token.tipo
            t = p

        match(token.tipo)

        if t is not None:
            t.branch[1] = exp()
    return t


def exp():
    pass
    global token
    t = simple_exp()

    if isLogic():
        p = newExpNode(ExpKind.OpK)

        if p is not None:
            p.branch[0] = t
            p.attr.op = token.tipo
            t = p

        match(token.tipo)

        if t is not None:
            t.branch[1] = simple_exp()
    return t


def simple_exp():
    pass
    global token
    t = term()

    while (token.tipo == "TKN_ADD") | (token.tipo == "TKN_MINUS"):
        p = newExpNode(ExpKind.OpK)

        if p is not None:
            p.branch[0] = t
            p.attr.op = token.tipo
            t = p

            match(token.tipo)
            t.branch[1] = term()
    return t


def term():
    pass
    global token

    t = factor()

    while (token.tipo == "TKN_MULTI") | (token.tipo == "TKN_DIV"):
        p = newExpNode(ExpKind.OpK)

        if p is not None:
            p.branch[0] = t
            p.attr.op = token.tipo
            t = p
            match(token.tipo)
            p.branch[1] = factor()
    return t


def factor():
    pass
    global token

    if token.tipo == "TKN_NUM":
        t = newExpNode(ExpKind.ConstK)

        if (t is None) & (token.tipo == "TKN_NUM"):
            try:
                valor = float(token.lexema)
                t.attr.val = valor
            except:
                print("No fue posible convertir el lexema a float")
        match("TKN_NUM")

    elif token.tipo == "TKN_ID":
        t = newExpNode(ExpKind.IdK)

        if (t is None) & (token.tipo == "TKN_ID"):
            t.attr.name = token.lexema

        match("TKN_ID")

    elif token.tipo == "TKN_ADD":
        t = newExpNode("TKN_MORE")

        if (t is None) & (token.tipo == "TKN_ID"):
            t.attr.name = token.lexema

        match("TKN_MORE")
        t.branch[0] = factor()

    elif token.tipo == "TKN_MINUS":
        t = newExpNode("TKN_MINUS")

        if (t is None) & (token.tipo == "TKN_ID"):
            t.attr.name = token.lexema

        match("TKN_MINUS")
        t.branch[0] = factor()

    elif token.tipo == "TKN_NOT":
        t = newExpNode("TKN_NOT")

        if (t is None) & (token.tipo == "TKN_ID"):
            t.attr.name = token.lexema

        match("TKN_NOT")
        t.branch[0] = factor()

    elif token.tipo == "TKN_LPAREN":
        match("TKN_LPAREN")
        t = exp()
        match("TKN_RPAREN")

    else:
        print("Syntax error, unexpected factor '" + token.lexema + "'" + " on line " + token.linea)
        output.write("Syntax error, unexpected factor '" + token.lexema + "'" + " on line " + token.linea + "\n")
        token = getToken()
    return t


def parse():
    global token
    t = TreeNode()
    token = getToken()
    t = stmt_sequence()
    return t


def main():
    pass
    t = parse()
    printTree(t)


def printTree(root):
    global output
    i = 0
    try:
        print(root.token.lexema)
        output.write(root.token.lexema + "\n")
        while root.branch[i] is not None:
            printBranch(root.branch[i], "   ")
            i += 1
    except:
        pass


def printBranch(root, tabulacion):
    global output
    print(tabulacion, root.token.lexema)
    output.write(tabulacion + root.token.lexema + "\n")
    i = 0
    try:
        while root.branch[i] is not None:
            printBranch(root.branch[i], tabulacion + "    ")
            i += 1
    except:
        pass

    i = 0
    try:
        while root.sibling[i] is not None:
            printBranch(root.sibling[i], tabulacion)
            i += 1
    except:
        pass


def printSibling(root, tabulacion):
    print(tabulacion, root.token.lexema)
    i = 0
    try:
        while root.branch[i] is not None:
            printBranch(root.branch[i], tabulacion + "    ")
            i += 1
    except:
        pass


try:
    output = open("Tree.txt", "w+")
    main()
    output.close()
except:
    pass
