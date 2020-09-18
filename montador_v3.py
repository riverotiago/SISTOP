##############################
#
# MONTADOR ABSOLUTO e REALOCAVEL
#
##############################

#=============================
# Definições
#=============================
# Instruções
INSTRUCOES = {
    "JP":0, "JZ":1, "JN":2, "LV":3, "+":4, "-":5, "*":6, "/":7, "LD":8,
    "MM":9, "SC":0xA, "RS":0xB, "HM":0xC, "GD":0xD, "PD":0xE, "OS":0xF
}
LISTA_INSTRUCOES = INSTRUCOES.keys()

# Pseudo-instruções
TAG_COMENTARIO = ";"
ORIGEM_ABSOLUTA = "@$"
ORIGEM_RELOCAVEL = "@"
FIM = "#"
CONSTANTE = "K"
EXTERNAL = "<"
ENTRY = ">"
OVERLAY = "overlay"
OVERLAYEND = "endoverlay"

# Valores
V_HEX = "/"
V_PLUSONE = "+1"

# Tamanho de montador
WORD_SIZE = 2 #Bytes

#=============================
# Imports
#=============================
import sys
import re
from string import whitespace


class Montador:
    def __init__(self):
        pass

    def tokenziar(self):
        """ Extrai label, instrução e operando de uma linha de código. """
        pass

    def primeiro_passo(self):
        """ Extrai as tabelas de símbolos, tabela de entry points,
            tabela de externals.
        """
        FIRST_ENDR = 0
        LAST_ENDR = 1

        tabela_simbolos = {}
        tabela_ext = {}
        tabela_ent = {}

        for linha in codigo:
            label, instru, op = tokenizar(linha)

            if ORIGEM_ABSOLUTA:
                pass
            elif ORIGEM_RELOCAVEL:
                pass
            elif FIM:
                pass
            elif CONSTANTE:
                pass
            elif EXTERNAL:
                pass
            elif ENTRY:
                pass
            elif OVERLAY:
                pass
            elif OVERLAYEND:
                pass
            else:
                pass

    def segundo_passo(self):
        """ Cria uma fila de montagem. """
        pass

    def montagem_absoluta(self):
        """ Cria um arquivo .hex carregável pelo loader. """
        pass

    def montagem_relocavel(self):
        """ Cria um arquivo .robj carregável pelo linker. """
        pass

    def montagem_loader(self):
        """ Cria um arquivo .hex carregável pela MVN. """
        pass
