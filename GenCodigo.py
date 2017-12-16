import pickle

output = open("code.tm", "w+")
mp = 0  # Memory Pointer
ac = 0  # Acumulator
TraceCode = 1

# Número de instrucción actúal
emitLoc = 0

# La más alta ubicación TM emitida hasta el momento. Para usar junto con emitSkip,
# emitirBackup y emitRestore
highEmitLoc = 0

# |------------------------------------------------------------------------|
# |         FUNCIONES NECESARIAS PARA LA EMISIÓN DE INSTRUCCIONES          |
# |------------------------------------------------------------------------|
# Imprime un comentario
def emitComment(comment):
    global output
    output.write("* ", comment, "\n")

# Imprime instrucciones de 'Solo Registro'
# TM instruction
# op = the opcode
# r = target register
# s = 1st source register
# t = 2nd source register
# c = a comment to be printed if TraceCode is 1
def emitRO(op, r, s, t, c):
    global output, highEmitLoc, emitLoc
    output.write(emitLoc, ":  ", op, "  ", r, ",", s, ",", t)
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
    output.write(emitLoc, ":  ", op, "  ", r, ",", d, "(", s, ")")
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

# | ------------------------------ FUNCIÓN PRINCIPAL -------------------------------------|
# | Si hemos llegado hasta este punto, es porque el Código Fuente ya está                 |
# | escrito correctamente (lexicamente, sintácticamente y gramáticalmente). Procedemos    |
# | a generar el código intermedio que posteriormente será la Entrada de la Tiny Machine  |
# | (quien se encargará de ensamblar nuestro código)                                      |
# | --------------------------------------------------------------------------------------|
def codeGen():
    global output, mp, ac
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

    output.close()


if __name__ == '__main__':
    codeGen()
