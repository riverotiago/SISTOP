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

class Endr:
    def __init__(self, value=0):
        self.value = value
        self.relocavel = 1

    def parse(self, val):
        if isinstance(val, int):
            return val
        else:
            if V_HEX in val:
                aux = val.replace(V_HEX,'')
                return int(aux, 16)
            else:
                raise Exception("Endereço é uma string")

    def absoluto(self, val):
        self.value = self.parse(val)
        self.relocavel = 0

    def relocavel(self, val):
        self.value = self.parse(val)
        self.relocavel = 1

    def add(self, val):
        self.value += self.parse(val)

    def copy(self, endr):
        self.value = endr.value
        self.relocavel = endr.relocavel

class Montador:
    def __init__(self):
        pass

    def parseop(self, op):
        if isinstance(op, int):
            # Valor decimal
            return op 
        elif V_HEX in val:
            aux = op.replace(V_HEX,'')
            # Valor hexadecimal
            return int(aux, 16)
        else:
            try:
                # Valor decimal
                return int(op)
            except:
                # String
                return op

    def tokenziar(self, linha):
        """ Extrai label, instrução e operando de uma linha de código. """
        # Setup
        linha_clean = re.sub(";.*","",linha)
        linha_split = linha_clean.strip().split() # Separa lista em blocos

        #Separa o comentário da linha se houver
        comentario = re.findall(";.*",linha)
        comentario = comentario[0] if comentario else ""

        # Inicializa
        label = instru = op = None
        tamanho = len(linha_split)

        # Checar se há label (Primeiro caracter não é nulo)
        if not linha_clean[0] in whitespace:
            label = linha_split[0]

        # Define a label, instrução e operando
        if label and tamanho == 3:
            instru = linha_split[1]
            op = linha_split[2]
        elif label and tamanho == 2:
            instru = linha_split[1]
            op = None
        elif not label and tamanho == 2:
            instru = linha_split[0]
            op = linha_split[1]
        elif not label and tamanho == 1:
            instru = linha_split[0]
            op = None

        if op != None:
            op = self.parseop(op)

        return label, instru, op, comentario

    #==========================
    # Tabela de Simbolos
    # label: [endr, relocavel]
    #==========================

    def solve_label(self, tabela_simbolos, label):
        return tabela_simbolos[label][0]

    def add_label(self, tabela_simbolos, label, endr_linha):
        tabela_simbolos[label] = [endr_linha.value, endr_linha.relocavel]
        pass

    #==========================
    # Passos
    #==========================

    def primeiro_passo(self):
        """ Extrai as tabelas de símbolos, tabela de entry points,
            tabela de externals.
        """
        FIRST_ENDR = 0
        LAST_ENDR = 1

        endr_linha = Endr()
        size_linha = 0

        tabela_simbolos = {}
        tabela_ext = {}
        tabela_ent = {}
        fila_listagem = []

        for linha in codigo:
            label, instru, op, comentario = self.tokenizar(linha)
            size_linha = 0

            if ORIGEM_ABSOLUTA:
                endr_linha.absoluto(op)
            elif ORIGEM_RELOCAVEL:
                endr_linha.relocavel(op)
            elif FIM:
                if op != None:
                    FIRST_ENDR = self.solve_label(tabela_simbolos, op)
            elif CONSTANTE:
                size_linha = WORD_SIZE//2
                if label:
                    self.add_label(tabela_simbolos, label, endr_linha)
            elif EXTERNAL:
                pass
            elif ENTRY:
                pass
            elif OVERLAY:
                pass
            elif OVERLAYEND:
                pass
            else:
                size_linha = WORD_SIZE

            endr_end_linha = endr_linha.value + size_linha
            self.add_listagem(fila_listagem, endr_linha.value, endr_end_linha, label, instru, op)

            
            endr_linha.add(size_linha)
            

    def segundo_passo(self, tabela_simbolos, tabela_ent, tabela_ext, fila_listagem):
        """ Processa uma fila de listagem e cria uma fila de montagem. """
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
