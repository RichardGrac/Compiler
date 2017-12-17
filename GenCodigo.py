import pickle

from TreeNode import *
from Hashtable import *

output = open("code.TM", "w+")
pc = 7  # Program Counter
mp = 6  # Memory Pointer. Apunta a la cima de la memoria (para almacenamientos temporales)
gp = 5  # Global Pointer. Apunta a lo más bajo de la memoria (para almacenamiento de variables)
ac = 0  # Acumulador
ac1 = 0  # Segundo Acumulador

# Habilitado/Deshabilitado para emisión de comentarios (se emitirán por default)
TraceCode = 1

# Número de instrucción actúal
emitLoc = 0

# La más alta ubicación TM emitida hasta el momento. Para usar junto con emitSkip,
# emitirBackup y emitRestore
highEmitLoc = 0

# tmpOffset es la compensación de memoria para los temporales. Se decrementa cada vez que
# se almacena un temp, y se incrementa cuando se carga de nuevo.
tmpOffset = 0

# Tabla de simbolos
hashtable = None


# |------------------------------------------------------------------------|
# |         FUNCIONES NECESARIAS PARA LA EMISIÓN DE INSTRUCCIONES          |
# |------------------------------------------------------------------------|
# Imprime un comentario
def emitComment(comment):
    global output
    # output.write("* " + comment + "\n")


# Imprime instrucciones de 'Solo Registro'
# TM instruction
# op = the opcode
# r = target register
# s = 1st source register
# t = 2nd source register
# c = a comment to be printed if TraceCode is 1
def emitRO(op, r, s, t, c):
    global output, highEmitLoc, emitLoc
    output.write(str(emitLoc) + ":  " + op + "  " + str(r) + "," + str(s) + "," + str(t))
    output.write("\n")
    emitLoc += 1
    if highEmitLoc < emitLoc:
        highEmitLoc = emitLoc
    # ./emitRO


# Imprime instrucciones de 'Memoria de Registro'
# TM instruction
#  * op = the opcode
#  * r = target register
#  * d = the offset
#  * s = the base register
#  * c = a comment to be printed if TraceCode is 1
def emitRM(op, r, d, s, c):
    global output, highEmitLoc, emitLoc
    output.write(str(emitLoc) + ":  " + op + "  " + str(r) + "," + str(d) + "(" + str(s) + ")")
    output.write("\n")
    emitLoc += 1
    if highEmitLoc < emitLoc:
        highEmitLoc = emitLoc
    # ./emitRM


# |------------------------------------------------------------------------|
# | LAS SIG. 3 INSTRUCCIONES SE EMPLEAN PARA SALTOS DE GENERACIÓN Y AJUSTE |
# |------------------------------------------------------------------------|

# Se utiliza para saltar un número de localidades que se ajustarán posteriormente, además de
# regresar a la localidad de instrucción actual, la cual se mantiene de manera interna dentro
# de GenCodigo.py. Por lo común esto se utiliza sólo en las llamadas 'emitSkip(1)', que salta
# una localidad simple que posteriormente será rellenada con una instrucción de salto, y
# emitSkip(0), que no salta localidades, sino que sólo es llamada para obtener la localidad
# de la instrucción actuala a fin de grabarla para una referencia posterior en un salto hacía
# atras.
def emitSkip(howMany):
    global highEmitLoc, emitLoc
    i = emitLoc
    emitLoc += howMany
    if highEmitLoc < emitLoc:
        highEmitLoc = emitLoc
    return i
    # ./emitSkip


# Se utiliza para establecer la localidad de la instrucción actual a una localidad anterior
# para ajuste.
def emitBackup(loc):
    global highEmitLoc
    if loc > highEmitLoc:
        emitComment("BUG in emitBackup")
        emitLoc = loc
    # ./emitBackup


# Se emplea para devolver la localidad de la instrucción actual al valor antes de una
# llamada a emitBackup
def emitRestore():
    global emitLoc, highEmitLoc
    emitLoc = highEmitLoc
    # ./emitRestore


# El procedimiento emitRM_Abs convierte una referencia absoluta en una referencia relativa
# a la PC al emitir una instrucción MT de registro en memoria.
# op = the opcode
# r = target register
# a = the absolute location in memory
# c = a comment to be printed if TraceCode is 1
def emitRM_Abs(op, r, a, c):
    global output, pc, highEmitLoc, emitLoc
    output.write(emitLoc + ":  " + op + "  " + r + "," + (a - (emitLoc + 1)) + "," + pc)
    output.write("\n")
    emitLoc += 1
    if highEmitLoc < emitLoc:
        highEmitLoc = emitLoc
# Regresa una dirección de código absoluta en una dirección relativa al pc al restar la
# localidad de instrucción actual más 1 (que es lo que será el pc durante la ejecución)
# desde el parámetro de localidad pasado, y utilizando el pc como el registro fuente.
# Por lo general será solo usada con una instrucción de salto condicional, como JEQ, o
# para generar un saldo incondicional empleando LDA y el pc como registro objetivo.
# ./emitRM_Abs

def st_lookup(lookup_var):
    global hashtable
    if lookup_var in hashtable:
        symbol = hashtable[lookup_var]
        return symbol.deep
    else:
        return -1

# ----------------------------------- GENERACIÓN DE CODIGO INTERMEDIO --------------------------------------------
# Genera el codigo de un nodo de Sentencia
def genStmt(tree):
    pass
    if tree.kind == StmtKind.IfK:
        if TraceCode == 1:
            emitComment("-> if")
        p1 = tree.branch[0]  # La expresión
        p2 = tree.sibling[0].branch[0]  # La parte verdadera

        # Generamos código para la expresión
        cGen(p1)
        savedLoc1 = emitSkip(1)
        emitComment("if: jump to else belongs here")
        # Recursividad de la parte del 'then'
        cGen(p2)
        savedLoc2 = emitSkip(1)
        emitSkip("if: jump to else belongs here")
        currentLoc = emitSkip(0)
        emitBackup(savedLoc1)
        emitRM_Abs("JEQ", ac, currentLoc, "if: jmp to else")
        emitRestore()
        # Recursividad de la parte del 'else'
        try:  # Puede no tener el else
            p3 = tree.sibling[1].branch[0]  # La parte falsacGen(p3)
            currentLoc = emitSkip(0)
            emitBackup(savedLoc2)
            emitRM_Abs("LDA", pc, currentLoc, "jmp to end")
        except Exception as e:
            print("Exception in IfK: ", e)
            pass
        if TraceCode == 1:
            emitComment("<- if")

    elif tree.kind == StmtKind.AssignK:
        if TraceCode == 1:
            emitComment("-> Assign")
        # Generamos código para rhs
        cGen(tree.branch[1])  # Evaluamos la Exp
        # Ahora guardamos el valor
        loc = st_lookup(tree.branch[0].token.lexema)  # Buscamos su locación dentro de la tabla de simbolos
        emitRM("ST", ac, loc, gp, "assig: store value")
        if TraceCode == 1:
            emitComment("<- Assign")

    elif tree.kind == StmtKind.CoutK:
        if TraceCode == 1:
            emitComment("-> CoutK")
        # Generamos código para la expresión a mostrar
        cGen(tree.branch[0])  # El valor, id u operador padre.
        # Lo mostramos ahora
        emitRO("OUT", ac, 0, 0, "write ac")


# Genera el codigo de un nodo de Expresión
def genExp(tree):
    pass
    if tree.kind == ExpKind.ConstK:
        if TraceCode == 1:
            emitComment("-> Const")
        # Generamos código para cargar una constante entera usando LDC
        emitRM("LDC", ac, tree.token.lexema, 0, "load const")
        if TraceCode == 1:
            emitComment("<- Const")

    elif tree.kind == ExpKind.IdK:
        if TraceCode == 1:
            emitComment("-> Id")
        loc = st_lookup(tree.token.lexema)
        emitRM("LD", ac, loc, gp, "load id value")
        if TraceCode == 1:
            emitComment("<- Id")


# cGen genera recursivamente el codigo dado el árbol
def cGen(tree):
    pass
    if tree is None:
        return
    try:
        if tree.nodeKind == NodeKind.StmtK:
            genStmt(tree)
        elif tree.nodeKind == NodeKind.ExpK:
            genExp(tree)
        cGen(tree.sibling[0])
    except Exception as e:
        # print("Exception in cGen: ", e)  # Siempre que no haya sibling ocurrirá, es normal.
        pass


# | ------------------------------ FUNCIÓN PRINCIPAL -------------------------------------|
# | Si hemos llegado hasta este punto, es porque el Código Fuente ya está                 |
# | escrito correctamente (lexicamente, sintácticamente y gramáticalmente). Procedemos    |
# | a generar el código intermedio que posteriormente será la Entrada de la Tiny Machine  |
# | (quien se encargará de ensamblar nuestro código)                                      |
# | --------------------------------------------------------------------------------------|
def codeGen():
    global output, mp, ac, hashtable
    try:
        # Obtenemos el árbol gramátical de la fase anterior:
        with open("gramatical_tree.bin", 'br') as f:
            tree = pickle.load(f)

        # Obtenemos la tabla de Simbolos de la fase anterior:
        with open("hashtable.bin", 'br') as f:
            hashtable = pickle.load(f)
    except Exception as e:
        print("Exception at GenCodigo(): ", e)
        pass

    emitComment("RICHARD&JOSUE Compilation to TM Code")
    # Generamos un preludio estandar
    emitComment("Preludio estandar:")
    emitRM("LD", mp, 0, ac, "load maxaddress from location 0")
    emitRM("ST", ac, 0, ac, "clear location 0")
    emitComment("End of standard prelude.")
    # Generamos el código para el programa Tiny
    cGen(tree.branch[0])
    # Terminamos
    emitComment("End of execution.")
    emitRO("HALT", 0, 0, 0, "")
    output.close()


if __name__ == '__main__':
    codeGen()
