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
        self._relocavel = 1

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
        self._relocavel = 0

    def relocavel(self, val):
        self.value = self.parse(val)
        self._relocavel = 1

    def add(self, val):
        self.value += self.parse(val)

    def copy(self, endr):
        self.value = endr.value
        self._relocavel = endr._relocavel

class Montador:
    def __init__(self):
        pass

    def parseop(self, op):
        if isinstance(op, int):
            # Valor decimal
            return op 
        elif V_HEX in op:
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

    def tokenizar(self, linha):
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
        return tuple(tabela_simbolos[label])

    def add_label(self, tabela_simbolos, label, endr_linha):
        tabela_simbolos[label] = [endr_linha.value, endr_linha._relocavel]
        pass

    #==========================
    # Passos
    #==========================

    def add_listagem(self,fila_listagem, endr, endr_end, label, instru, op):
        pass

    def primeiro_passo(self, codigo):
        """ Extrai as tabelas de símbolos, tabela de entry points,
            tabela de externals.
        """
        FIRST_ENDR = 0
        LAST_ENDR = 1

        endr_linha = Endr()
        size_linha = 0

        # Overlays
        overlay_endr_linha = Endr()
        register_overlay = False
        overlay_table = {}
        overlay_n = 0

        tabela_simbolos = {}
        tabela_ext = {}
        tabela_ent = {}
        fila_listagem = []

        for linha in codigo:
            label, instru, op, comentario = self.tokenizar(linha)
            size_linha = 0

            # Trata símbolos encontrados
            if ORIGEM_ABSOLUTA == instru:
                endr_linha.absoluto(op)
            elif ORIGEM_RELOCAVEL == instru:
                endr_linha._relocavel(op)
            elif FIM == instru:
                if op != None:
                    FIRST_ENDR,_ = self.solve_label(tabela_simbolos, op)
            elif CONSTANTE == instru:
                size_linha = WORD_SIZE//2
                if label:
                    self.add_label(tabela_simbolos, label, endr_linha)
            elif EXTERNAL == instru:
                pass
            elif ENTRY == instru:
                pass
            elif OVERLAY == instru:
                register_overlay = True
                overlay_n = op
                overlay_table[overlay_n] = [] # Cria fila de listagem do overlay_n
                overlay_endr_linha.relocavel(0) # Re-inicializa o endereço relc. para 0
            elif OVERLAYEND == instru:
                register_overlay = False
            else:
                size_linha = WORD_SIZE

            if register_overlay:
                endr_end_linha = overlay_endr_linha.value + size_linha - 1
                self.add_listagem(overlay_table[overlay_n], endr_linha.value, endr_end_linha, label, instru, op)
                ov_endr_linha.add(size_linha)
            else:
                endr_end_linha = endr_linha.value + size_linha - 1
                self.add_listagem(fila_listagem, endr_linha.value, endr_end_linha, label, instru, op)
                endr_linha.add(size_linha)

        return tabela_simbolos, tabela_ent, tabela_ext, fila_listagem, overlay_table

    def segundo_passo(self, tabela_simbolos, tabela_ent, tabela_ext, fila_listagem):
        """ Processa uma fila de listagem e cria uma fila de montagem. """

        for tokens in fila_listagem:
            # Recebe tokens
            endr, endr_end, label, instru, op = tokens

            endr_rel = op_rel = True
            
            # Resolve labels no operando
            if op in tabela_simbolos:
                op, op_rel = self.solve_label(tabela_simbolos, op)

            # Monta fila de montagem <-- TODO
            

    def montagem_absoluta(self):
        """ Cria um arquivo .hex carregável pelo loader. """
        pass

    def montagem_relocavel(self):
        """ Cria um arquivo .robj carregável pelo linker. """
        pass

    def montagem_loader(self):
        """ Cria um arquivo .hex carregável pela MVN. """
        pass
