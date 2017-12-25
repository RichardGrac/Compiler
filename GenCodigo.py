# ┌----------------------------------------- GENERACIÓN DE CÓDIGO ------------------------------------------------┐
# | Dado el árbol gramátical (no necesario, pudo haber sido el sintáctico) generarémos el código intermedio PARA  |
# | LA MAQUINA TINY (TM), el cúal hará "la simulación" de código ensamblador, con lo cúal terminaremos nuestro    |
# | terminaremos nuestro compilador.                                                                              |
# | Este archivo es prácticamente la traducción de CODE.C, CODE.H, CGEN.C y CGEN.H de "Tiny Compiler by Louden    |
# | con adición del repeat-until y cambios de->ahora:        read->cin, write->cout, repeat->while                |
# └---------------------------------------------------------------------------------------------------------------┘

import pickle
import sys

from TreeNode import *
from Hashtable import *

output = open("code.RJI", "w+")
pc = 7  # Program Counter
mp = 6  # Memory Pointer. Apunta a la cima de la memoria (para almacenamientos temporales)
gp = 5  # Global Pointer. Apunta a lo más bajo de la memoria (para almacenamiento de variables)
ac = 0  # Acumulador
ac1 = 1  # Segundo Acumulador

# Habilitado/Deshabilitado para emisión de comentarios (se emitirán por default)
TraceCode = 0

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

# La var 'sibling' será usada como variable controladora de la navegación entre Nodos. No siempre es el Siguiente nodo
# es el que hay que verificar. Ejm: if-else


# |------------------------------------------------------------------------|
# |         FUNCIONES NECESARIAS PARA LA EMISIÓN DE INSTRUCCIONES          |
# |------------------------------------------------------------------------|
# Imprime un comentario
def emitComment(comment):
    global output, TraceCode
    if TraceCode == 1:
        output.write("* " + comment + "\n")


# Imprime instrucciones de 'Solo Registro'
# TM instruction
# op = the opcode
# r = target register
# s = 1st source register
# t = 2nd source register
# c = a comment to be printed if TraceCode is 1
def emitRO(op, r, s, t, c):
    global output, highEmitLoc, emitLoc, TraceCode
    if TraceCode == 0:
        c = ""  # No se emitirá comentario
    # output.write(str(emitLoc) + ":  " + op + "  " + str(r) + "," + str(s) + "," + str(t) + " " + c)
    output.write(str(emitLoc) + " " + op + " " + str(r) + " " + str(s) + " " + str(t) + "" + c)
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
    global output, highEmitLoc, emitLoc, TraceCode
    if TraceCode == 0:
        c = ""  # No se emitirá comentario
    # output.write(str(emitLoc) + ":  " + op + "  " + str(r) + "," + str(d) + "(" + str(s) + ") " + c)
    output.write(str(emitLoc) + " " + op + " " + str(r) + " " + str(d) + " " + str(s) + "" + c)
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
    global highEmitLoc, emitLoc
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
    global output, pc, highEmitLoc, emitLoc, TraceCode
    if TraceCode == 0:
        c = ""  # No se emitirá comentario
    # output.write(str(emitLoc) + ":  " + op + "  " + str(r) + " " + str(a - (emitLoc + 1)) + "(" + str(pc) + ") " + c)
    output.write(str(emitLoc) + " " + op + " " + str(r) + " " + str(a - (emitLoc + 1)) + " " + str(pc) + "" + c)
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
    global pc, mp, gp, ac, ac1, TraceCode, emitLoc, highEmitLoc, tmpOffset
    sibling = 0
    pass
    if tree.kind == StmtKind.IfK:
        if TraceCode == 1:
            emitComment("-> if")
        p1 = tree.branch[0]  # La expresión
        p2 = tree.sibling[0].branch[0]  # La parte verdadera

        # Generamos código para la expresión
        cGen(p1)

        # ----- Aquí debería ir la condicional de salto. Por lo que la generaremos despues, así como en el While -----
        savedLoc1 = emitSkip(0)
        emitLoc += 1  # Reservamos su espacio de la condicional

        # Generamos codigo de la parte Verdadera
        cGen(p2)

        # Locación despúes de generar el código de la parte Verdadera (es decir, locación de else)
        savedLoc2 = emitSkip(0)

        # -------------------- Volvemos atrás para CREAR la evaluación --------------------------------------------
        emitLoc = savedLoc1
        # Ya nos posicionamos atrás en el código, ahora hacemos la evaluación.
        emitRM_Abs("JEQ", ac, (savedLoc2+1), "if: jmp to else")  # Salta a savedLoc2 si se cumple
        # <- Es savedLoc2+1 porque en savedLoc2 hay un salto incondicional (el que hace que termine el if)
        # ------------------------------ Fin del pasado  ----------------------------------------------------------
        # Nos posicionamos a donde deberíamos de ir
        emitLoc = savedLoc1 + (savedLoc2 - savedLoc1)

        # Hacemos un salto incondiciconal despues del else cuando terminamos el if (o si no hay else, igual se hace)
        savedLoc3 = emitSkip(0)
        emitLoc += 1  # Reservamos el espacio para ese salto incondicional

        # Generamos código de la parte 'else'
        try:  # Puede no tener el else
            if tree.sibling[1].token.tipo == "TKN_ELSE":
                p3 = tree.sibling[1].branch[0]  # La parte falsa
                cGen(p3)
                sibling = 2  # Retornamos el sibling[2] para cuando en cGen tengamos que posicionarnos en el Nodo siguiente
            else:
                sibling = 1
        except Exception as e:
            print("Exception in IfK: ", e)
            sibling = 1  # Si cayó en el except, es porque no hubo parte 'else'. Mandamos '1' para posicionarnos después

        # Guardamos posición actual:
        savedLoc4 = emitSkip(0)
        # Nos posicionamos antes del else para poder hacer el salto a savedLoc4
        emitLoc = savedLoc3
        emitRM_Abs("LDA", pc, savedLoc4, "jmp after else (if exists)")
        # Nos reposicionamos donde deberiamos ir
        emitLoc = savedLoc3 + (savedLoc4 - savedLoc3)

        if TraceCode == 1:
            emitComment("<- if")

    # Este caso se hizo de manera más manual que otros (excepto if)
    elif tree.kind == StmtKind.WhileK:
        if TraceCode == 1:
            emitComment("-> While")

        p1 = tree.branch[0]  # Expresión
        p2 = tree.branch[1]  # Cuerpo
        savedLoc0 = emitSkip(0)  # Antes de generar la expresión
        # Generamos la expresión
        cGen(p1)  # Gen de Código de expresión

        # --------- Aquí debería ir la condicional de salto. Por lo que lo dejaremos para despues, guardando su ------
        savedLoc1 = emitSkip(0)  # ubicación actual (para poder volver. Contiene el actúal emitLoc)


        emitLoc += 1  # Brincamos una posición para continuar emitiendo código (reservando la posición anterior)
        # Emitimos código del Body
        cGen(p2)
        savedLoc2 = emitSkip(0)  # Guardamos ubicación actual (Posterior a la generación del Body y el salto incond.)

        # Hacemos salto hacía antes de cargar la evaluación
        emitRM_Abs("LDA", pc, savedLoc0, "jmp to while evaluation")
        savedLoc2 += 1

        # -------------------- Volvemos atrás para CREAR la evaluación --------------------------------------------
        emitLoc = savedLoc1
        # Ya estamos posicionados atrás, evaluamos:
        emitRM_Abs("JEQ", ac, savedLoc2, "while: if true continue")  # salta a savedLoc2 si Verdadero (o sea, continua)
        # ------------------------------ Fin del pasado  ----------------------------------------------------------

        # Nos posicionamos a donde deberíamos de ir
        emitLoc = savedLoc1 + (savedLoc2 - savedLoc1)

        if TraceCode == 1:
            emitComment("<- While")


    elif tree.kind == StmtKind.AssignK:
        if TraceCode == 1:
            emitComment("-> Assign")
        # Generamos código para rhs
        cGen(tree.branch[1])  # Evaluamos la Exp
        # Ahora guardamos el valor
        loc = st_lookup(tree.branch[0].token.lexema)  # Buscamos su locación dentro de la tabla de simbolos
        emitRM("ST", ac, loc, gp, "assign: store value")
        if TraceCode == 1:
            emitComment("<- Assign")

    elif tree.kind == StmtKind.CoutK:
        if TraceCode == 1:
            emitComment("-> CoutK")
        # Generamos código para la expresión a mostrar
        cGen(tree.branch[0])  # El valor, id u operador padre.
        # Lo mostramos ahora
        emitRO("OUT", ac, 0, 0, "write ac")
        if TraceCode == 1:
            emitComment("<- CoutK")

    elif tree.kind == StmtKind.RepeatK:
        if TraceCode == 1:
            emitComment("-> Repeat")
        p1 = tree.branch[0]
        p2 = tree.sibling[0].branch[0]
        savedLoc1 = emitSkip(0)
        emitComment("repeat: jump after body comes back here")
        # Generamos código para el Cuerpo
        cGen(p1)
        # Generamos código para ver si ya se cumplió la condición
        cGen(p2)
        emitRM_Abs("JEQ", ac, savedLoc1, "repeat: jmp back to body")
        sibling = 1
        if TraceCode == 1:
            emitComment("<- Repeat")

    elif tree.kind == StmtKind.CinK:
        emitRO("IN", ac, 0, 0, "read integer value")
        loc = st_lookup(tree.branch[0].token.lexema)
        emitRM("ST", ac, loc, gp, "read: store value")

    return sibling

# Genera el código necesario para los saltos condicionales/incondicionales dependiendo el tipo de op. booleano
def is_boolean_operator(instruction, message):
    global ac, ac1, pc
    emitRO("SUB", ac, ac1, ac, message)
    emitRM(instruction, ac, 2, pc, "br if true")
    emitRM("LDC", ac, 0, ac, "false case")
    emitRM("LDA", pc, 1, pc, "unconditional jmp")
    emitRM("LDC", ac, 1, ac, "true case")


# Debido a que la Tiny Machine no ensambla valores flotantes, tendrémos que trabajar con Enteros :(
def get_integer(lexema):
    pass
    try:
        # return int(float(lexema))
        return lexema
    except Exception as e:
        print("Exception casting a value (def get_integer())")


# Genera el codigo de un nodo de Expresión
def genExp(tree):
    global pc, mp, gp, ac, ac1, TraceCode, emitLoc, highEmitLoc, tmpOffset
    pass
    if tree.kind == ExpKind.ConstK:
        if TraceCode == 1:
            emitComment("-> Const")
        # Generamos código para cargar una constante entera usando LDC
        integer = get_integer(tree.token.lexema)
        emitRM("LDC", ac, str(integer), 0, "load const")
        if TraceCode == 1:
            emitComment("<- Const")

    elif tree.kind == ExpKind.IdK:
        if TraceCode == 1:
            emitComment("-> Id")
        loc = st_lookup(tree.token.lexema)
        emitRM("LD", ac, loc, gp, "load id value")
        if TraceCode == 1:
            emitComment("<- Id")

    elif tree.kind == ExpKind.OpK:
        if TraceCode == 1:
            emitComment("-> Op")
        p1 = tree.branch[0]
        p2 = tree.branch[1]
        # Generación de código para el argumento izquierdo
        cGen(p1)
        # Generación de código para hacer push al operando izquierdo
        emitRM("ST", ac, tmpOffset, mp, "op: push left")
        tmpOffset -= 1
        # Generación de código para el operando derecho
        cGen(p2)
        # Ahora cargamos al operando izquierdo
        tmpOffset += 1
        emitRM("LD", ac1, tmpOffset, mp, "op: load left")

        if tree.token.tipo == "TKN_ADD":
            emitRO("ADD", ac, ac1, ac, "op +")

        elif tree.token.tipo == "TKN_MINUS":
            emitRO("SUB", ac, ac1, ac, "op -")

        elif tree.token.tipo == "TKN_MULTI":
            emitRO("MUL", ac, ac1, ac, "op *")

        elif tree.token.tipo == "TKN_DIV":
            emitRO("DIV", ac, ac1, ac, "op /")

        elif tree.token.tipo == "TKN_LESS":
            is_boolean_operator("JLT", "op <")

        elif tree.token.tipo == "TKN_ELESS":
            is_boolean_operator("JLE", "op <=")

        elif tree.token.tipo == "TKN_EQUAL":
            is_boolean_operator("JEQ", "op ==")

        elif tree.token.tipo == "TKN_MORE":
            is_boolean_operator("JGT", "op >")

        elif tree.token.tipo == "TKN_EMORE":
            is_boolean_operator("JGE", "op >=")

        elif tree.token.tipo == "TKN_NEQUAL":
            is_boolean_operator("JNE", "op !=")

        else:
            emitComment("BUG: Unknown operator")
        if TraceCode == 1:
            emitComment("<- Op")


# cGen genera recursivamente el codigo dado el árbol
def cGen(tree):
    pass
    if tree is None:
        return
    try:
        sibling = 0
        if tree.nodeKind == NodeKind.StmtK:
            sibling = genStmt(tree)
        elif tree.nodeKind == NodeKind.ExpK:
            genExp(tree)
        cGen(tree.sibling[sibling])
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
        # with open("gramatical_tree.bin", 'br') as f:
        #     tree = pickle.load(f)

        # Obtenemos el árbol gramátical de la fase anterior como argumento mandado por el IDE:
        with open(sys.argv[1], 'br') as f:
            tree = pickle.load(f)

        # Obtenemos la tabla de Simbolos de la fase anterior:
        # with open("hashtable.bin", 'br') as f:
        #     hashtable = pickle.load(f)

        # Obtenemos la tabla de Simbolos de la fase anterior como argumento mandado por el IDE:
        with open(sys.argv[2], 'br') as f:
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
