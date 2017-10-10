from TreeNode import *
import pickle
import sys

# Se necesita de guardar la variables y la profundidad, así como el Nodo con sus atributos por lo que
# haré una hashtable para la VARIABLE-PROFUNDIDAD y otro con la VARIABLE-SIMBOLO
# Tabla de simbolos
class Symbol:
    pass

    def __init__(self, name=None, deep=None, line=[], val=None, dtype=None, node=None):
        self.name = name
        self.deep = deep
        self.lines = line
        self.val = val
        self.dtype = dtype
        self.Node = node


errores = []
primitivo = None  # TKN_BOOLEAN, TKN_INT, TKN_REAL
deepTable = {}  # Contenedor de VARIABLE-PROFUNDIDAD
symbolsTable = {}  # Contenedor de VARIABLE-SIMBOLO


def kill_instance_variables(deep):
    global deepTable, symbolsTable
    remove = []
    # Guardamos todas las claves con la profundidad que buscamos eliminar
    for clave in deepTable:
        if deepTable[clave] == deep:
            remove.append(clave)

    # Eliminamos todas esas claves-valores
    for rmv in remove:
        # print("Variable '" + rmv + "' deleted")
        del deepTable[rmv]
        del symbolsTable[rmv]


def does_variable_exist(t):
    global errores
    if t.token.lexema in symbolsTable:  # O tambien "if t.token.lexema in deepTable"
        return True
    else:
        # print("Gramatical error, variable '" + t.token.lexema + "' is not defined at line", str(t.token.linea))
        errores.append("Gramatical error, variable '" + t.token.lexema + "' is not defined at line " +
                       str(t.token.linea))
        return False


def get_primitive(t, deep):
    if t.token.lexema in symbolsTable:
        symbol = symbolsTable[t.token.lexema]
        return symbol.Node.attr.tipe
    else:
        errores.append("Gramatical error, variable '" + t.token.lexema + "' is not defined at line " +
                       str(t.token.linea))
        # print("Gramatical error, variable '" + t.token.lexema + "' is not defined at line " + str(t.token.linea))


# def isLogicSemantic(token):
#     if (token.tipo == "TKN_LESS") | (token.tipo == "TKN_ELESS"):
#         return True
#     elif (token.tipo == "TKN_EQUAL") | (token.tipo == "TKN_NEQUAL"):
#         return True
#     elif (token.tipo == "TKN_MORE") | (token.tipo == "TKN_EMORE"):
#         return True
#     else:
#         return False


# def is_operator_correct(tipo, token):
#     if tipo == "boolean":
#         return isLogicSemantic(token)
#     else:
#         return not isLogicSemantic(token)


def validate_consts(token):
    if (token.tipo == "TKN_NUM") | (token.tipo == "TKN_ID"):
        if (token.lexema.__contains__(".")) & (primitivo == "int"):
            # print("Possible loss of precision at line", str(token.linea))
            return int(float(token.lexema))
            # return "error"
        elif primitivo == "int":
            return int(token.lexema)

        if primitivo == "boolean":
            if (token.lexema == "1") | (token.lexema == "0"):
                return int(token.lexema)
            else:
                return "error"
        return float(token.lexema)
    else:
        return "error"


def is_type_correct(t, deep):
    global primitivo
    if primitivo == "int":
        if get_primitive(t, deep) == "int":
            return True
        elif get_primitive(t, deep) == "real":
            # perdida de precisión
            return True
        else:
            return False
    elif primitivo == "real":
        if get_primitive(t, deep) == "int":
            return False
        elif get_primitive(t, deep) == "real":
            # perdida de precisión
            return True
        else:
            return False
    elif primitivo == "boolean":
        pass

    if get_primitive(t, deep) == primitivo:
        return True
    else:
        return False


def validate_exp_tree(t, deep):
    global primitivo, errores
    if t is None:
        return

    if t.kind == ExpKind.OpK:
        token = t.token
        # primitivo = get_primitive(t, deep)

        # if not is_operator_correct(primitivo, token):
        #     print("The token", t.token.lexema, "doesn't corresponds to", primitivo)

        # else:
        val1 = validate_exp_tree(t.branch[0], deep)
        val2 = validate_exp_tree(t.branch[1], deep)
        if (val1 is not "error") & (val2 is not "error"):
            if token.lexema == "+":
                return val1 + val2
            elif token.lexema == "-":
                return val1 - val2
            elif token.lexema == "*":
                return val1 * val2
            elif (token.lexema == "/") & (primitivo == "int"):
                # print("Possible loss of precision at line ", str(token.linea))  # token.lexema
                return int(val1/val2)
            elif token.lexema == "/":
                return val1 / val2
        else:
            return "error"


    elif t.kind == ExpKind.ConstK:
        return validate_consts(t.token)

    elif t.kind == ExpKind.IdK:
        if does_variable_exist(t):
            if not is_type_correct(t, deep):
                # print("It is not posible to perform the assignment " + primitivo + " -> " + t.token.lexema)
                errores.append("Gramatical error, '" + t.token.lexema + "' can not be '" + primitivo + "' "
                                                                                "at line " + t.token.linea)
            else:
                # Lo sacamos del symbolsTable y actualizamos linea en la que reaparecio la variable
                symbol = symbolsTable[t.token.lexema]
                update_symbolsTable(t, symbol.val, 0)
                # Aparentemente se lo seteamos como una Constante
                t.token.lexema = str(symbol.val)
                return validate_consts(t.token)
        else:
            return "error"

    validate_exp_tree(t.branch[0], deep)
    validate_exp_tree(t.branch[1], deep)


def make_variable(t, deep):
    if t is None:
        return
    token = t.token
    if t.token.lexema in symbolsTable:
        # print("Gramatical error: variable " + token.lexema + " is already defined at line", str(t.token.linea))
        errores.append("Gramatical error: variable " + token.lexema + " is already defined at line" +
                       str(t.token.linea))
    else:
        symbolsTable[token.lexema] = Symbol(token.lexema, deep, [token.linea], None, t.attr.tipe, t)
        deepTable[token.lexema] = deep
        # print(t.attr.tipe, token.lexema)

    try:
        tAux = t.sibling[0]
        make_variable(tAux, deep)
    except Exception as e:
        # print("Excepcion: t.sibling[0] nulo")
        pass


def isLogicSecondOrder(token):
    if (token.tipo == "TKN_LESS") | (token.tipo == "TKN_ELESS"):
        return True
    elif (token.tipo == "TKN_EQUAL") | (token.tipo == "TKN_NEQUAL"):
        return True
    elif (token.tipo == "TKN_MORE") | (token.tipo == "TKN_EMORE"):
        return True
    else:
        return False


def validate_boolean_expresion(t, deep):
    global primitivo
    token = t.token
    if isLogicSecondOrder(token):
        val1 = validate_exp_tree(t.branch[0], deep)
        val2 = validate_exp_tree(t.branch[1], deep)
        if (val1 is not "error") & (val2 is not "error"):
            if token.lexema == "<":
                if val1 < val2:
                    return True
                else:
                    return False
            elif token.lexema == "<=":
                if val1 <= val2:
                    return True
                else:
                    return False
            elif token.lexema == "<=":
                if val1 <= val2:
                    return True
                else:
                    return False
            elif token.lexema == ">":
                if val1 > val2:
                    return True
                else:
                    return False
            elif token.lexema == ">=":
                if val1 >= val2:
                    return True
                else:
                    return False
            elif token.lexema == "==":
                if val1 == val2:
                    return True
                else:
                    return False
            elif token.lexema == "!=":
                if val1 != val2:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return "error"

    elif t.kind == ExpKind.IdK:
        # primitivo = "boolean"
        if (does_variable_exist(t)) & (get_primitive(t, deep) == "boolean"):
            return
        else:
            # print("Gramatical error, incorrect assignment at line", str(t.token.linea))
            return "error"
    elif t.kind == ExpKind.ConstK:
        return validate_consts(t.token)
    else:
        # print("Gramatical error, incorrect use of the boolean expression at line", str(t.token.linea))
        errores.append("Gramatical error, incorrect use of the boolean expression at line " + str(t.token.linea))


# Conjunto de boolean_expression y exp
def validate_cout_expression(t, deep):
    global primitivo
    token = t.token
    val = ""
    if isLogicSecondOrder(token):
        val = validate_boolean_expresion(t, deep)
    else:
        val = validate_exp_tree(t, deep)

    if val is not "error":
        # print("cout expression := ", val)
        pass
    elif val is "error":
        # print("Grama")
        pass


def update_symbolsTable(t, val, msg):
    t.attr.val = val
    # Sacamos el simbolo y actualizamos su información
    symbol = symbolsTable[t.token.lexema]
    symbol.lines.append(t.token.linea)
    symbol.val = val
    symbolsTable[t.token.lexema] = symbol

    if msg == 1:
        # Ocurre cuando hay una creacion o modificacion del valor de la variable, si msg==0 es porque
        # solo modificamos la linea en donde reapareció alguna variable (no imprimimos nuevo valor)
        # print(t.token.lexema, ":=", str(val))
        pass


def node_secuence(t, deep):
    global primitivo, errores
    sibling = 0
    if t is None:
        return

    if t.nodeKind == NodeKind.StmtK:
        if t.kind == StmtKind.MainK:
            node_secuence(t.branch[0], (deep + 1))
            # kill_instance_variables(deep + 1)

        elif t.kind == StmtKind.IfK:
            primitivo = "real"
            val = validate_boolean_expresion(t.branch[0], (deep + 1))
            if val is True:
                # print("'if' expression True at line", t.branch[0].token.linea)
                pass
            elif val is False:
                # print("'if' expression False at line", t.branch[0].token.linea)
                pass
            else:
                pass
            kill_instance_variables(deep + 1)
            node_secuence(t.sibling[0].branch[0], (deep + 1))
            kill_instance_variables(deep + 1)
            sibling = 1
            try:  # Puede no tener el else
                node_secuence(t.sibling[1].branch[0], (deep + 1))
                kill_instance_variables(deep + 1)
                sibling = 2
            except Exception as e:
                # print("Exception in IfK:", e)
                pass

        elif t.kind == StmtKind.CoutK:
            # primitivo = "real"
            # get_primitive(t.branch[0], deep)
            validate_cout_expression(t.branch[0], deep)

        elif t.kind == StmtKind.AssignK:
            if does_variable_exist(t.branch[0]):
                primitivo = get_primitive(t.branch[0], deep)
                if primitivo == "boolean":
                    val = validate_boolean_expresion(t.branch[1], deep)
                    if val is not "error":
                        update_symbolsTable(t.branch[0], val, 1)
                    else:
                        # print("Gramatical error, incorrect assignment at line", str(t.branch[1].token.linea))
                        errores.append("Gramatical error, incorrect assignment at line " +
                                       str(t.branch[1].token.linea))

                else:
                    val = validate_exp_tree(t.branch[1], deep)
                    if val is not "error":
                        if get_primitive(t.branch[0], deep) == "real":
                            update_symbolsTable(t.branch[0], "{0:.2f}".format(val), 1)
                        else:
                            update_symbolsTable(t.branch[0], val, 1)
                    else:
                        # print("Gramatical error, incorrect assignment at line", str(t.branch[1].token.linea))
                        errores.append("Gramatical error, incorrect assignment at line " +
                                       str(t.branch[1].token.linea))
            else:
                pass


        elif t.kind == StmtKind.CinK:
            does_variable_exist(t.branch[0])

        elif t.kind == StmtKind.DeclK:
            make_variable(t.branch[0], deep)

        elif t.kind == StmtKind.RepeatK:
            node_secuence(t.branch[0], (deep + 1))
            kill_instance_variables(deep + 1)
            val = validate_boolean_expresion(t.sibling[0].branch[0], (deep + 1))
            kill_instance_variables(deep + 1)
            sibling = 1

        elif t.kind == StmtKind.WhileK:
            val = validate_boolean_expresion(t.branch[0], (deep + 1))
            node_secuence(t.branch[1], (deep + 1))
            kill_instance_variables(deep + 1)
            sibling = 2

    try:
        # sibling normalmente será 0, excepto si viene del IfK/repeatK(será 1) y si tiene o no parte else(será 2)
        tAux = t.sibling[sibling]
        node_secuence(tAux, deep)
    except Exception as e:
        # print("Excepcion:", e)
        pass


def printHashtable(output, errores, symbolsTable):
    for error in errores:
        output.write(error + " \n")

    output.write("\nNombre_variable-Localidad-Numero_linea-Valor-Tipo\n")
    for symbol in symbolsTable:
        output.write(symbolsTable[symbol].name + "-" + str(symbolsTable[symbol].deep) + "-"
                     + str(symbolsTable[symbol].lines) + "-" + str(symbolsTable[symbol].val) + "-"
                     + symbolsTable[symbol].dtype + "\n")
        print(symbolsTable[symbol].name + "-" + str(symbolsTable[symbol].deep) + "-"
                     + str(symbolsTable[symbol].lines) + "-" + str(symbolsTable[symbol].val) + "-"
                     + symbolsTable[symbol].dtype)


def printErrors(errores):
    for error in errores:
        print(error)


def semantico():
    global symbolsTable, errores
    try:
        output = open("Hashtable.txt", "w+")

        # Para leer desde binario:
        with open("tree.bin", 'rb') as f:
            t = pickle.load(f)

        # Para leer desde argumento, leo el archivo serializado que viene en los argumentos,
        # se deserealiza y se iguala a la variable 't' para continuar con el analisis semantico:
        # with open(sys.argv[1], 'rb') as f:
        #     t = pickle.load(f)

        node_secuence(t, 0)
        printErrors(errores)  # Errores en consola
        printHashtable(output, errores, symbolsTable)  # Errores y tabla en Hashtable.txt
        output.close()
    except Exception as e:
        # print("Exception at semantico(): ", e)
        pass


if __name__ == '__main__':
    semantico()
