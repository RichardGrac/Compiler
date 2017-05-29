import os
import time


def verifica(tipo):
    band = True
    if tipo == "lexico":
        output = open("Tokens.txt", "r")
        for line in output:
            linea, columna, type, lexema = line.split(" ")
            if type == "TKN_ERROR":
                band = False
    elif tipo == "sintactico":
        output = open("Tree.txt", "r")
        for line in output:
            if "Syntax error" in line:
                band = False

    if band:
        print("Analisis " + tipo + " exitoso")
    else:
        print("Error en análisis " + tipo + ".")
    return band

try:
    os.system("Lexico.py")
    # verifica("lexico")
    time.sleep(0.09)
    os.system("Sintactico.py")
    # verifica("sintactico")
    pass

except:
    print("Problema al intentar ejecutar algun archivo")
    pass
