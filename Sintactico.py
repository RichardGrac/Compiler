from TreeNode import *
import sys
import pickle

# ------------------------------------- INICIO DE ANALIZADOR SINTÁCTICO -----------------------------

tokens = []  # Todos los tokens salidos del Léxico
token = None  # Token actual
contador = 0  # Para recorrer los tokens

# Leer el archivo de entrada como argumento (En conjunto con IDE(Java)):
filepath = sys.argv[1]
output = open(filepath, "r")

# Para leer desde txt:
# output = open("Tokens.txt", "r")

for line in output:
    linea, columna, tipo, lexema = line.split(" ")
    tok = Token(linea, columna, tipo, lexema[:-1])  # Substring hasta -1 porque agregaba "\n"
    if tok.tipo != "TKN_ERROR":
        tokens.append(tok)


def match(expected):
    pass
    global token
    if expected == token.tipo:
        token = getToken()
    else:
        print("Syntax error, unexpected '" + token.lexema + "' was expected: " + expected +
              " before column " + token.columna + " at line " + token.linea)
        output.write("Syntax error, unexpected '" + token.lexema + "' was expected: " + expected +
                     " before column " + token.columna + " at line " + token.linea + "\n")


def getToken():
    pass
    global contador, tokens
    if contador < len(tokens):
        tok = tokens[contador]
        contador += 1
        return tok
    else:
        tok = tokens[contador - 1]
        linea = tok.linea
        columna = int(tok.columna) + 1
        tok = Token(linea, str(columna), "TKN_EOF", "EOF")
        return tok  # End of file


def scanto(synchset):
    global token
    while True:
        if token.tipo == "TKN_EOF":
            break
        elif not token.tipo in synchset:
            token = getToken()
        else:
            break
    return


def checkinput(firstset, followset):
    global token
    if not token.tipo in firstset:
        print("Syntax error, unexpected '" + token.lexema + "' before column " + token.columna + " at line "
              + token.linea)
        output.write("Syntax error, unexpected '" + token.lexema + "' before column " + token.columna + " at line "
                     + token.linea + "\n")
        scanto(firstset + followset)
    return


def newStmtNode(kind):
    pass
    global token
    t = TreeNode()
    t.token = token

    # No recuerdo porqué 3 veces, pero atribuimos el tipo de nodo > Statement y el subtipo > IfK, CoutK, DeclK...
    i = 0
    while i < 3:
        t.nodeKind = NodeKind.StmtK
        t.kind = kind
        i += 1
    return t


def newExpNode(ExpKind):
    pass
    global token
    t = TreeNode()
    t.token = token

    # Lo mismo que en newStmtNode
    i = 0
    while i < 3:
        t.nodeKind = NodeKind.ExpK
        t.kind = ExpKind
        i += 1
    return t


# --------------- Declaración de funciones ---------------------
def main():
    pass
    global token, tokens
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
                # tokAux = tokens[contador-1]
                # longitud = (float(tokAux.columna) + len(tokAux.lexema))-1
                # print("Syntax error, was expected '}' after column " + longitud + " at line " + tokAux.linea)
                # output.write("Syntax error, was expected '}' after column " + tokAux.columna + " at line " +
                #              tokAux.linea + "\n")
                pass

    return t


def stmt_sequence(synchset):
    pass
    global token
    t = TreeNode()
    t = statement(synchset)
    p = t

    while (token.tipo != "TKN_RBRACE") & (token.tipo != "TKN_EOF"):
        q = statement(synchset)

        if q is not None:
            if t is None:
                p = q
                t = p
            else:
                p.sibling.append(q)
                p = q
    return t


def statement(synchset):
    pass
    global token
    t = TreeNode()
    firstset = ["TKN_IF", "TKN_WHILE", "TKN_REPEAT", "TKN_CIN", "TKN_COUT", "TKN_LBRACE", "TKN_ID", "TKN_INT",
                "TKN_REAL",
                "TKN_BOOLEAN"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = TreeNode()
        if token.tipo == "TKN_ID":
            t = assign_stmt(synchset + ["TKN_IF", "TKN_WHILE", "TKN_REPEAT", "TKN_CIN", "TKN_COUT", "TKN_LBRACE",
                                        "TKN_INT", "TKN_REAL", "TKN_BOOLEAN"])

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

        elif token.tipo == "TKN_REPEAT":
            t = repeat_stmt(synchset)

            # checkinput(synchset, firstset)
    return t


def block(synchset):
    pass
    global token
    firstset = ["TKN_LBRACE", "TKN_IF", "TKN_WHILE", "TKN_REPEAT", "TKN_CIN", "TKN_COUT", "TKN_ID"]
    synchset += []
    checkinput(firstset, synchset)

    t = TreeNode()
    if not token.tipo in synchset:
        match("TKN_LBRACE")
        t = stmt_sequence(synchset)
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
        tipo = token.tipo
        match(token.tipo)

        # Mejoramos el tipo de atributo que será
        if tipo == "TKN_INT":
            tipo = "int"
        elif tipo == "TKN_REAL":
            tipo = "real"
        elif tipo == "TKN_BOOLEAN":
            tipo = "boolean"

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
            # Si solo es un TKN_ID, atribuimos a q. Si son más, atribuimos a p y lo enlazamos con q
            if not flag:
                q.attr.name = token.lexema
                q.attr.tipe = tipo
            else:
                p.attr.name = token.lexema
                p.attr.tipe = tipo
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
            t.branch[0] = expresion(["TKN_SEMICOLON", "TKN_RPAREN", "TKN_THEN"])
            match("TKN_RPAREN")

        if token.tipo == "TKN_THEN":
            t.sibling.append(newStmtNode(StmtKind.ThenK))
        else:
            tAux = token
            token = Token(token.linea, token.columna, "TKN_THEN", "then")
            t.sibling.append(newStmtNode(StmtKind.ThenK))
            token = tAux
        match("TKN_THEN")

        if t is not None:
            t.sibling[0].branch[0] = block(["TKN_ELSE", "TKN_RBRACE"])

        if token.lexema == "else":
            t.sibling.append(newStmtNode(StmtKind.ElseK))
            match("TKN_ELSE")

            if t is not None:
                t.sibling[1].branch[0] = block(["TKN_RBRACE"])

                # t.sibling.append(statement(synchset))
                # checkinput(synchset, firstset)
    return t


def while_stmt(synchset):
    pass
    global token
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
            t.branch[1] = block(["TKN_RBRACE"])
            # checkinput(synchset, firstset)
    return t


def repeat_stmt(synchset):
    pass
    global token
    firstset = ["TKN_REPEAT"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        t = newStmtNode(StmtKind.RepeatK)
        match("TKN_REPEAT")

        if t is not None:
            t.branch[0] = block(["TKN_UNTIL", "TKN_RBRACE"])

        if token.tipo == "TKN_UNTIL":
            t.sibling.append(newStmtNode(StmtKind.UntilK))
        else:
            tAux = token
            token = Token(token.linea, token.columna, "TKN_UNTIL", "until")
            t.sibling.append(newStmtNode(StmtKind.UntilK))
            token = tAux
        match("TKN_UNTIL")

        if t is not None:
            match("TKN_LPAREN")
            t.sibling[0].branch[0] = expresion(["TKN_SEMICOLON", "TKN_RPAREN"])
            match("TKN_RPAREN")

        match("TKN_SEMICOLON")
        # checkinput(synchset, firstset)
    return t


def assign_stmt(synchset):
    pass
    global token, tokens, contador
    t = TreeNode()
    firstset = ["TKN_ID"]
    synchset += []
    checkinput(firstset, synchset)

    if not token.tipo in synchset:
        q = newStmtNode(StmtKind.AssignK)

        if q is not None:
            q.attr.name = token.lexema
        match("TKN_ID")

        # Caso especial de que sea ++ o -- Haremos lo sig: --> id := id + 1
        if (token.tipo == "TKN_PPLUS") | (token.tipo == "TKN_LLESS"):
            lex = token.lexema[0]  # + o -
            if lex == "+":
                tipo = "TKN_ADD"
            else:
                tipo = "TKN_MINUS"

            # Creamos tokens Artificiales y añadimos a tokens[]
            tokenA = tokens[contador - 2]  # id
            tokenB = Token(token.linea, token.columna, tipo, lex)  # - o +
            tokenC = Token(token.linea, token.columna, "TKN_NUM", "1")  # 1

            # Establecemos nodo de asignación :=
            token = Token(token.linea, token.columna, "TKN_ASSIGN", ":=")
            tokens[contador - 1] = token  # Actualizamos array, cambiando el PPLUS por ":="
            t = newStmtNode(StmtKind.AssignK)
            match("TKN_ASSIGN")

            if t is not None:
                t.attr.name = token

            # Añado a tokens[]:
            tokens.insert(contador - 1, tokenA)
            tokens.insert(contador, tokenB)
            tokens.insert(contador + 1, tokenC)
            token = tokens[contador - 1]
            # contador -= 1

            if t is not None:
                t.branch[0] = q
                t.branch[1] = expresion(synchset + ["TKN_SEMICOLON", "TKN_RPAREN"])

        # Si no, es una asignación
        else:
            if token.tipo == "TKN_ASSIGN":
                t = newStmtNode(StmtKind.AssignK)
            else:
                tAux = token
                token = Token(token.linea, token.columna, "TKN_ASSIGN", ":=")
                t = newStmtNode(StmtKind.AssignK)
                token = tAux
            match("TKN_ASSIGN")

            # t = newStmtNode(StmtKind.AssignK)
            if t is not None:
                t.attr.name = token
            # match("TKN_ASSIGN")

            if t is not None:
                t.branch[0] = q
                t.branch[1] = expresion(synchset + ["TKN_SEMICOLON", "TKN_RPAREN"])

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
    t = TreeNode()
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
    t = TreeNode()
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
                # En caso de que haya dos operadores seguidos:
                while (token.tipo == "TKN_ADD") | (token.tipo == "TKN_MINUS"):
                    print("Syntax error, multiple operator detected at column " + token.columna + " at line " +
                          token.linea)
                    output.write("Syntax error, multiple operator detected at column " + token.columna +
                                 " at line " + token.linea + "\n")
                    token = getToken()
                t.branch[1] = term(synchset)
        checkinput(synchset, firstset)
    return t


def term(synchset):
    pass
    global token
    t = TreeNode()
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
                while (token.tipo == "TKN_MULTI") | (token.tipo == "TKN_DIV"):
                    print("Syntax error, multiple operator detected at column " + token.columna + " at line " +
                          token.linea)
                    output.write("Syntax error, multiple operator detected at column " + token.columna +
                                 " at line " + token.linea + "\n")
                    token = getToken()
                p.branch[1] = factor(synchset)
        checkinput(synchset, firstset)
    return t


def factor(synchset):
    pass
    global token
    t = TreeNode()
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
    return t


def printTree(root):
    global output
    #serializo el objeto root y lo guardo en el archivo 'tree.bin'
    with open('tree.bin', 'wb') as f:
        pickle.dump(root, f)
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


# Quitamos errores que se repitan de una misma linea
def cleanErrorFile():
    errores = []
    noErrores = []
    # Separamos errores del árbol
    try:
        output = open("Tree.txt", "r")
        for line in output:
            if "Syntax error" in line:
                errores.append(line[:-1])
            else:
                noErrores.append(line[:-1])
        output.close()
    except:
        print("Problema en txt - cleanErrorFile()")
        pass

    # Quitamos errores duplicados
    errores2 = []
    try:
        atLine = "asdasdasxx"
        for error in errores:
            if not atLine in error[-7:]:
                errores2.append(error)
                atLine = error[-7:]
            if "EOF" in error:
                errores2.append(error)
    except:
        print("Problema en txt - cleanErrorFile()")
        pass

    # Juntamos los errores con el árbol
    try:
        output = open("Tree.txt", "w+")
        for error in errores2:
            output.write(error + "\n")
        for valido in noErrores:
            output.write(valido + "\n")
        output.close()
    except:
        print("Problema al escribir txt - cleanErrorFile()")


# Iniciamos programa:
def init_sintactic():
    global output
    try:
        output = open("Tree.txt", "w+")
        tree = main1()
        output.close()
        cleanErrorFile()
        return tree
    except Exception as e:
        print("Error en el main: ", e)
        pass


# Si se llama unicamente el archivo "Sintactico.py":
# Cuando se llama desde el Análisis gramátical se va directamente a init_sintactic.
if __name__ == '__main__':
    init_sintactic()


# NOTA: para que muestre el árbol en el IDE habrá que descomentar las lineas referentes al -print- dentro de
# printTree(), printSibling y printBranch