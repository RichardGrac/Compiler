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
    elif tipo == "gramatical":
        output = open("Hashtable.txt")
        for line in output:
            if "Gramatical error" in line:
                band = False

    if band:
        print("Analisis " + tipo + " exitoso")
    else:
        print("Error en análisis " + tipo + ".")
    return band


try:
    os.system("Lexico.py")
    if verifica("lexico"):
        time.sleep(0.09)
        os.system("Sintactico.py")
        if verifica("sintactico"):
            time.sleep(0.1)
            os.system("Gramatical.py")
            verifica("gramatical")
except:
    print("Problema al intentar ejecutar algun archivo")
    pass
