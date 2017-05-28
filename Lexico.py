import sys
from enum import Enum


class STATE(Enum):
    pass
    # Estados generales
    ERROR = 0
    BEGGIN = 1
    END = 2
    # Comentario Simple | Comentario multiple
    SIMPLE_COMMENT = 3
    IN_MULTIPLE_COMMENT = 4
    IN_MULTIPLE_COMMENT_END = 5  # Asterisco antes de cerrar
    # Operadores
    ADDITION = 6
    SUBSTRACTION = 7
    DIFFERENCE = 8
    MULTIPLICATION = 9
    # Operadores logicos
    DOUBLE_ADDITION = 10
    DOUBLE_SUBSTRACTION = 11
    # Cadena
    IN_STRING = 12
    # Numeros
    IN_NUMERAL = 13
    IN_FLOAT = 14
    # Comparacion
    IN_LESS = 15
    IN_GREATER = 16
    IN_NEGATION = 17
    IN_ASSIGNMENT = 18
    IN_EQUAL = 19


# Fin clase STATE

# Agrega la información del Token: fila col tipoToken CaracteresDesde(punteroAntiguo-punteroActual)
# (Suma 1 por cuestiones de formato)
def appendWithOne(tkn):
    global estado
    arreglo.append(str(lineaActual) + " " + str(colActual - (contador - cont_inicial)) + " " + tkn +
                   " " + linea[cont_inicial:contador + 1])
    estado = STATE.END


def append(tkn):
    global estado
    arreglo.append(str(lineaActual) + " " + str(colActual - (contador - cont_inicial)) + " " + tkn +
                   " " + linea[cont_inicial:contador])
    decreasing()
    estado = STATE.END


def decreasing():
    global contador, colActual
    contador -= 1
    colActual -= 1


# ----------------------------------- INICIO DE ANALISIS LEXICO ------------------------------
# fileLocation = sys.argv[1]
# print(fileLocation)
archivo = open("Input.txt")
# archivo = open(fileLocation)
linea = archivo.read()
linea += "\n"
archivo.close()

pReservadas = {
    "main": "TKN_MAIN",
    "if": "TKN_IF",
    "then": "TKN_THEN",
    "else": "TKN_ELSE",
    # "end": "TKN_END",
    "do": "TKN_DO",
    "while": "TKN_WHILE",
    "repeat": "TKN_REPEAT",
    "until": "TKN_UNTIL",
    "cin": "TKN_CIN",
    "cout": "TKN_COUT",
    "real": "TKN_REAL",
    "int": "TKN_INT",
    "boolean": "TKN_BOOLEAN"}

sEspeciales = {
    '(': "TKN_LPAREN",
    ')': "TKN_RPAREN",
    '{': "TKN_LBRACE",
    '}': "TKN_RBRACE",
    ';': "TKN_SEMICOLON",
    ',': "TKN_COMMA"}

estado = STATE.BEGGIN  # TOKEN en el que se encuentra
cont_inicial = 0  # Contará las posiciones desde la última
contador = 0  # Puntero que recorrerá el texto
lineaActual = 1  # Linea del archivo en la que se encuentra
lineasExtras = 0  # Contará los \n de un bloque de comentarios
colActual = 1  # Contador de columna en que se encuentra
arreglo = []
errores = []
keys = sEspeciales.keys()  # Contendrá todas las llaves para los simbolos especiales
keys2 = pReservadas.keys()  # Contendrá todas las llaves para las palabras reservadas

# Cuando hago contador -= 1 es porque vamos a repetir la lectura de ese caracter que rompió con la secuencia del
# token anterior encontrado. colActual -= 1 para seguir con el correcto conteo.

while contador < len(linea):
    caracter = linea[contador]
    # INICIO DE AUTÓMATA
    if estado == STATE.BEGGIN:
        if ((caracter >= 'A') & (caracter <= 'Z')) | ((caracter >= 'a') & (caracter <= 'z')) | (caracter == '_'):
            estado = STATE.IN_STRING
        elif (caracter >= '0') & (caracter <= '9'):
            estado = STATE.IN_NUMERAL
        elif (caracter == ' ') | (caracter == '\t') | (caracter == '\n'):
            colActual += 1
            if caracter == '\n':
                lineaActual += 1
                colActual = 1
            cont_inicial = (contador + 1)
            contador += 1
            continue
        elif caracter == '/':
            estado = STATE.DIFFERENCE
        elif caracter == '+':
            # appendWithOne("TKN_ADD")
            estado = STATE.ADDITION
        elif caracter == '-':
            estado = STATE.SUBSTRACTION
            # appendWithOne("TKN_MINUS")
        elif caracter == '<':
            estado = STATE.IN_LESS
        elif caracter == '>':
            estado = STATE.IN_GREATER
        elif caracter == ':':
            estado = STATE.IN_ASSIGNMENT
        elif caracter == '!':
            estado = STATE.IN_NEGATION
        elif caracter == '=':
            estado = STATE.IN_EQUAL
        elif caracter == '*':
            appendWithOne("TKN_MULTI")
        elif caracter == '%':
            appendWithOne("TKN_PERCENT")
        elif caracter in keys:
            appendWithOne(sEspeciales.get(caracter))
        else:
            estado = STATE.ERROR  # Estado de Error
    elif estado == STATE.IN_STRING:
        if ((caracter < 'A') | (caracter > 'Z')) & ((caracter < 'a') | (caracter > 'z')) & \
                ((caracter < '0') | (caracter > '9')) & (caracter != '_'):
            if linea[cont_inicial:contador] in keys2:
                append(pReservadas.get(linea[cont_inicial:contador]))
            else:
                append("TKN_ID")
    elif estado == STATE.IN_NUMERAL:
        if caracter == '.':
            if (linea[contador + 1] >= '0') & (linea[contador + 1] <= '9'):
                estado = STATE.IN_FLOAT
            else:
                estado = STATE.ERROR
        elif (caracter < '0') | (caracter > '9'):
            append("TKN_NUM")
    elif estado == STATE.IN_FLOAT:
        if (caracter < '0') | (caracter > '9'):
            append("TKN_NUM")
    elif estado == STATE.DIFFERENCE:
        if caracter == '*':
            estado = STATE.IN_MULTIPLE_COMMENT
        elif caracter == '/':
            estado = STATE.END  # Forma de terminar
            while (contador < len(linea)) & (linea[contador] != '\n'):
                contador += 1
            # Quitamos todos los caracteres que continuan en la linea
            while linea[cont_inicial] == '\n':
                cont_inicial += 1
            lineaActual += 1
            colActual = 1
        else:
            append("TKN_DIV")
    elif estado == STATE.IN_MULTIPLE_COMMENT:
        if caracter == '*':
            estado = STATE.IN_MULTIPLE_COMMENT_END
        elif caracter == "\n":
            lineasExtras += 1
    elif estado == STATE.IN_MULTIPLE_COMMENT_END:
        if caracter == "\n":
            lineasExtras += 1
        if caracter == '/':
            estado = STATE.END  # Terminó, volvemos al estado inicial
            # appendWithOne("TKN_COMMENT")
            if linea[contador + 1] == '\n':
                cont_inicial += 1
            lineaActual += lineasExtras
            lineasExtras = 0
        elif caracter == '*':
            estado = STATE.IN_MULTIPLE_COMMENT_END
        else:
            estado = STATE.IN_MULTIPLE_COMMENT
    elif estado == STATE.ADDITION:
        if caracter == '+':
            appendWithOne("TKN_PPLUS")
        # elif (caracter >= '0') & (caracter <= '9'):  # Para numeros con signo +3
        #     estado = STATE.IN_NUMERAL
        #     decreasing()
        else:
            append("TKN_ADD")
    elif estado == STATE.SUBSTRACTION:
        if caracter == '-':
            appendWithOne("TKN_LLESS")
    #     # elif (caracter >= '0') & (caracter <= '9'):  # Para numeros con signo -3
    #     #     estado = STATE.IN_NUMERAL
    #     #     decreasing()
        else:
            append("TKN_MINUS")
    elif estado == STATE.IN_LESS:
        if caracter == '=':
            appendWithOne("TKN_ELESS")
        else:
            append("TKN_LESS")
    elif estado == STATE.IN_GREATER:
        if caracter == '=':
            appendWithOne("TKN_EMORE")
        else:
            append("TKN_MORE")
    elif estado == STATE.IN_ASSIGNMENT:
        if caracter == '=':
            appendWithOne("TKN_ASSIGN")
        else:
            decreasing()
            estado = STATE.ERROR
    elif estado == STATE.IN_NEGATION:
        if caracter == '=':
            appendWithOne("TKN_NEQUAL")
        else:
            decreasing()
            estado = STATE.ERROR
    elif estado == STATE.IN_EQUAL:
        if caracter == '=':
            appendWithOne("TKN_EQUAL")
        else:
            decreasing()
            estado = STATE.ERROR
    if estado == STATE.END:
        cont_inicial = (contador + 1)
        estado = STATE.BEGGIN
    if estado == STATE.ERROR:
        appendWithOne("TKN_ERROR")
        cont_inicial = (contador + 1)
        estado = STATE.BEGGIN
    contador += 1
    colActual += 1
    # FIN DE AUTÓMATA (while)

# Si está en estado de error el ultimo caracter/linea no es valido(a) o
# si está en un estado NO TERMINANTE (DIF. de END o BEGGIN) hubo Comentario multiple sin cerrar
if (estado == STATE.ERROR) | ((estado != STATE.END) & (estado != STATE.BEGGIN)):
    decreasing()
    if (estado == STATE.IN_MULTIPLE_COMMENT) | (estado == STATE.IN_MULTIPLE_COMMENT_END):
        arreglo.append(str(lineaActual) + " " + str(colActual) + " TKN_ERROR " + "[Comentario]")
    else:
        appendWithOne("TKN_ERROR")

for tokens in arreglo:
    print(tokens)

output = open("Tokens.txt", "w+")
for tokens in arreglo:
    output.write(tokens + "\n")
output.close()
