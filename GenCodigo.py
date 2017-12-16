from TreeNode import *
import pickle
import sys


# | ------------------------------ FUNCIÓN PRINCIPAL -------------------------------------|
# | Si hemos llegado hasta este punto, es porque el Código Fuente ya está                 |
# | escrito correctamente (lexicamente, sintácticamente y gramáticalmente). Procedemos    |
# | a generar el código intermedio que posteriormente será la Entrada de la Tiny Machine  |
# | (quien se encargará de ensamblar nuestro código)                                      |
# | --------------------------------------------------------------------------------------|
def genCodigo():
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
    print("Hello World!")


if __name__ == '__main__':
    genCodigo()
