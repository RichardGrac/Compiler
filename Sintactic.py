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
    ElseK = 10


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
        tok = Token(0, 0, "TKN_EOF", "EOF")
        return tok  # End of file


def scanto(synchset):
    global token
    while True:
        if token.tipo == "EOF":
            break
        elif not token.tipo in synchset:
            token = getToken()
        else:
            break
    return


def checkinput(firstset, followset):
    global token
    if not token.tipo in firstset:
        print("Syntax error at line: " + token.linea + ", unexpected " + token.lexema)
        scanto(firstset + followset)
    return


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


# --------------- Declaración de funciones ---------------------
def main():
    pass
    global token
    t = TreeNode()

    if token.tipo == "TKN_EOF":
        print("Empty file")
    else:
        firstset = ["TKN_MAIN"]
        synchset = ["TKN_EOF"]
        checkinput(firstset, synchset)

        if not token.tipo in synchset:
            t = newStmtNode(StmtKind.MainK)
            match("TKN_MAIN")
            match("TKN_LBRACE")

            if t is not None:
                t.branch[0] = stmt_sequence(["TKN_RBRACE"])
            try:
                match("TKN_RBRACE")
            except:
                pass
    return t


def stmt_sequence(synchset):
    pass
    global token
    t = TreeNode()
    # firstset = ["TKN_IF", "TKN_WHILE", "TKN_DO", "TKN_CIN", "TKN_COUT", "TKN_RBRACE", "TKN_ID", "TKN_INT", "TKN_REAL",
    #             "TKN_BOOLEAN"]
    # synchset = ["TKN_RBRACE"]
    # checkinput(firstset, synchset)
    #
    # while True:
    #     if not token.tipo in synchset:
    t = statement(synchset)
    p = t
    #
    while (token.tipo != "TKN_RBRACE") & (token.tipo != "TKN_EOF"):
        q = statement(synchset)

        if q is not None:
            if t is None:
                p = q
                t = p
            else:
                p.sibling.append(q)
                p = q
    # # checkinput(synchset, firstset)
    #         if token == "EOF":
    #             break
    #     else:
    #         break

    return t


def statement(synchset):
    pass
    global token
    t = TreeNode()
    firstset = ["TKN_IF", "TKN_WHILE", "TKN_DO", "TKN_CIN", "TKN_COUT", "TKN_LBRACE", "TKN_ID", "TKN_INT", "TKN_REAL",
                "TKN_BOOLEAN"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = TreeNode()
        if token.tipo == "TKN_ID":
            t = assign_stmt(synchset)

        elif token.tipo == "TKN_IF":
            t = if_stmt(synchset)

        elif token.tipo == "TKN_CIN":
            t = cin_stmt(synchset)

        elif token.tipo == "TKN_COUT":
            t = cout_stmt(synchset)

        elif (token.tipo == "TKN_REAL") | (token.tipo == "TKN_INT") | (token.tipo == "TKN_BOOLEAN"):
            t = declaration_stmt(synchset)

        elif token.tipo == "TKN_LBRACE":
            t = block(synchset)

        elif token.tipo == "TKN_WHILE":
            t = while_stmt(synchset)

        elif token.tipo == "TKN_DO":
            t = do_stmt(synchset)

            # checkinput(synchset, firstset)
    return t


def block(synchset):
    pass
    global token
    firstset = ["TKN_LBRACE"]
    synchset += ["TKN_ELSE", "TKN_UNTIL"]
    checkinput(firstset, synchset)

    t = TreeNode()
    if not token.tipo in synchset:
        match("TKN_LBRACE")
        t = stmt_sequence(["TKN_RBRACE"])
        match("TKN_RBRACE")
        # checkinput(synchset, firstset)
    return t


def declaration_stmt(synchset):
    pass
    global token
    firstset = ["TKN_INT", "TKN_REAL", "TKN_BOOLEAN"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = newStmtNode(StmtKind.DeclK)
        match(token.tipo)

        w = newStmtNode(StmtKind.AssignK)
        t.branch[0] = w
        flag = False

        while token.tipo == "TKN_ID":  # Posterior a la Declaracion debe seguirle un ID por lo menos
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

            q.attr.name = token.lexema
            q.attr.tipe = token.lexema
            if flag:
                q.sibling.append(p)

            match("TKN_ID")
            if token.tipo == "TKN_COMMA":  # Es error si pone dos o más ID's sin coma
                match("TKN_COMMA")
            else:
                break
            flag = True
        # checkinput(synchset, firstset)
        match("TKN_SEMICOLON")
    return t


def if_stmt(synchset):
    pass
    global token
    firstset = ["TKN_IF"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = newStmtNode(StmtKind.IfK)
        match("TKN_IF")

        if t is not None:
            match("TKN_LPAREN")
            t.branch[0] = expresion(["TKN_SEMICOLON", "TKN_RPAREN"])
            match("TKN_RPAREN")


        match("TKN_THEN")

        if t is not None:
            t.branch[1] = block(["TKN_ELSE", "TKN_UNTIL", "TKN_RBRACE"])

        if token.lexema == "else":
            # t.branch[2] = newStmtNode(StmtKind.ElseK)
            match("TKN_ELSE")

            if t is not None:
                t.branch[2] = block(["TKN_ELSE", "TKN_UNTIL", "TKN_RBRACE"])

                # t.sibling.append(statement(synchset))
                # checkinput(synchset, firstset)
    return t


def while_stmt(synchset):
    firstset = ["TKN_WHILE"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = newStmtNode(StmtKind.WhileK)
        match("TKN_WHILE")

        if t is not None:
            match("TKN_LPAREN")
            t.branch[0] = expresion(["TKN_SEMICOLON", "TKN_RPAREN"])
            match("TKN_RPAREN")

        if t is not None:
            t.branch[1] = block(["TKN_ELSE", "TKN_UNTIL", "TKN_RBRACE"])
            # checkinput(synchset, firstset)
    return t


def do_stmt(synchset):
    firstset = ["TKN_DO"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = newStmtNode(StmtKind.DoK)
        match("TKN_DO")

        if t is not None:
            t.branch[0] = block(["TKN_ELSE", "TKN_UNTIL", "TKN_RBRACE"])

        match("TKN_UNTIL")

        if t is not None:
            match("TKN_LPAREN")
            t.branch[1] = expresion(["TKN_SEMICOLON", "TKN_RPAREN"])
            match("TKN_RPAREN")

        match("TKN_SEMICOLON")
        # checkinput(synchset, firstset)
    return t


def assign_stmt(synchset):
    pass
    global token
    firstset = ["TKN_ID"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        q = newStmtNode(StmtKind.AssignK)

        if q is not None:
            q.attr.name = token.lexema
        match("TKN_ID")

        t = newStmtNode(StmtKind.AssignK)
        if t is not None:
            t.attr.name = token
        match("TKN_ASSIGN")

        if t is not None:
            t.branch[0] = q
            t.branch[1] = expresion(["TKN_SEMICOLON", "TKN_RPAREN"])

        match("TKN_SEMICOLON")
        # checkinput(synchset, firstset)
    return t


def cin_stmt(synchset):
    pass
    global token
    firstset = ["TKN_CIN"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = newStmtNode(StmtKind.CinK)
        match("TKN_CIN")

        if t is not None:
            t.attr.name = token.lexema
            t.branch[0] = newExpNode(ExpKind.IdK)
        match("TKN_ID")

        match("TKN_SEMICOLON")
        # checkinput(synchset, firstset)
    return t


def cout_stmt(synchset):
    pass
    global token
    firstset = ["TKN_COUT"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = newStmtNode(StmtKind.CoutK)
        match("TKN_COUT")

        if t is not None:
            t.branch[0] = expresion(["TKN_SEMICOLON", "TKN_RPAREN"])

        match("TKN_SEMICOLON")
        # checkinput(synchset, firstset)
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


def expresion(synchset):
    pass
    global token
    firstset = ["TKN_LPAREN", "TKN_ID", "TKN_NUM"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = simple_exp(synchset)

        if isLogic():
            p = newExpNode(ExpKind.OpK)

            if p is not None:
                p.branch[0] = t
                p.attr.op = token.tipo
                t = p

            match(token.tipo)

            if t is not None:
                t.branch[1] = simple_exp(synchset)
        checkinput(synchset, firstset)
    return t


def simple_exp(synchset):
    pass
    global token
    firstset = ["TKN_LPAREN", "TKN_NUM", "TKN_ID"]
    synchset += ["TKN_LESS", "TKN_ELESS", "TKN_MORE", "TKN_EMORE", "TKN_EQUAL", "TKN_NEQUAL"]
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = term(synchset)

        while (token.tipo == "TKN_ADD") | (token.tipo == "TKN_MINUS"):
            p = newExpNode(ExpKind.OpK)

            if p is not None:
                p.branch[0] = t
                p.attr.op = token.tipo
                t = p

                match(token.tipo)
                t.branch[1] = term(synchset)
        checkinput(synchset, firstset)
    return t


def term(synchset):
    pass
    global token
    firstset = ["TKN_LPAREN", "TKN_NUM", "TKN_ID"]
    synchset += ["TKN_ADD", "TKN_MINUS"]
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = factor(synchset)

        while (token.tipo == "TKN_MULTI") | (token.tipo == "TKN_DIV"):
            p = newExpNode(ExpKind.OpK)

            if p is not None:
                p.branch[0] = t
                p.attr.op = token.tipo
                t = p
                match(token.tipo)
                p.branch[1] = factor(synchset)
        checkinput(synchset, firstset)
    return t


def factor(synchset):
    pass
    global token
    firstset = ["TKN_LPAREN", "TKN_NUM", "TKN_ID"]
    synchset += ["TKN_MULTI", "TKN_DIV"]
    if not token.tipo in synchset:

        if token.tipo == "TKN_NUM":
            t = newExpNode(ExpKind.ConstK)
            if t is None:
                try:
                    valor = float(token.lexema)
                    t.attr.val = valor
                except:
                    print("No fue posible convertir el lexema a float")
            match("TKN_NUM")

        elif token.tipo == "TKN_ID":
            t = newExpNode(ExpKind.IdK)
            if t is None:
                t.attr.name = token.lexema
            match("TKN_ID")

        elif token.tipo == "TKN_LPAREN":
            match("TKN_LPAREN")
            t = expresion(["TKN_SEMICOLON", "TKN_RPAREN"])
            match("TKN_RPAREN")

        # else:
        #     print("Syntax error, unexpected factor '" + token.lexema + "'" + " on line " + token.linea)
        #     output.write("Syntax error, unexpected factor '" + token.lexema + "'" + " on line " + token.linea + "\n")
        #     token = getToken()

        # checkinput(synchset, firstset)
    return t


def parse():
    global token
    t = TreeNode()
    token = getToken()
    t = main()
    return t


def main1():
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


# Iniciamos programa:
try:
    output = open("Tree.txt", "w+")
    main1()
    output.close()
except:
    pass
