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
    "MM":9, "SC":0xA, "RS":0xB, "HM":0xC, "GD":0xD, "PD":0xE, "OS":0xF,
    ">>":0x10,"<<":0x11,"&&":0x12, "CP":0x13, "JPE":0x14, "JPNE": 0x15
}
OP_ABS_INSTRUCOES = ["LV", "K", "OS", "CP", ">>", "<<", "&&"]
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

    def add_listagem(self,fila_listagem, endr, endr_end, endr_rel, label, instru, op):
        """ Cria uma lista listagem e a adiciona a fila. """
        listagem = [endr, endr_end, endr_rel, label, instru, op]
        fila_listagem.append(listagem)

    # < --- TODO --- Facilitar a extração de overlays
    # variável register_overlay precisa estar no contexto de primeiro passo e analisar linha
    def analisar_linha1(self, string_linha, endr_linha,  fila_listagem, tabela):
        """ Extrai dados de uma linha de código para as tabelas e para a listagem. """
        label, instru, op, comentario = self.tokenizar(string_linha)
        if label == None and instru == None and op == None:
            return False

        #//////////////////////////////
        #// Declaração 
        FIRST_ENDR = 0
        size_linha = 0
        register_line = False
        register_overlay = False

        #//////////////////////////////
        #// Decisão
        if ORIGEM_ABSOLUTA == instru:
            endr_linha.absoluto(op)

        elif ORIGEM_RELOCAVEL == instru:
            endr_linha._relocavel(op)

        elif FIM == instru:
            pass

        elif CONSTANTE == instru:
            register_line = True
            size_linha = WORD_SIZE//2

        elif EXTERNAL == instru:
            pass

        elif ENTRY == instru:
            pass

        elif OVERLAY == instru:
            register_overlay = True
            overlay_n = op
            tabela['overlay'][overlay_n] = {'meta':[], 'listagem':[]} # Cria fila de listagem do overlay_n

        elif OVERLAYEND == instru:
            register_overlay = False

        else:
            # Trata instruções não pseudo
            register_line = True
            size_linha = WORD_SIZE+1

        #//////////////////////////////
        #// Extrai label
        if label:
            self.add_label(tabela['simbolos'], label, endr_linha)

        #//////////////////////////////
        #// Registro de listagem
        if register_overlay: # Separa o overlay do resto do código
            tabela['overlay'][overlay_n]['listagem'].append( string_linha )

        elif register_line:
            endr_end_linha = endr_linha.value + size_linha - 1
            self.add_listagem(fila_listagem, endr_linha.value, endr_end_linha, \
                                endr_linha._relocavel,label, instru, op)
            endr_linha.add(size_linha)

        return endr_linha 


    def primeiro_passo(self, codigo):
        """ Extrai as tabelas de símbolos, tabela de entry points,
            tabela de externals.
        """
        print("/"*50,f"\n// Primeiro passo\n")
        endr_linha = Endr()
        size_linha = 0

        # Overlays
        register_overlay = False
        overlay_endr_linha = Endr()
        overlay_n = 0

        # Tabelas
        overlay_table = {}
        tabela_simbolos = {}
        tabela_ext = {}
        tabela_ent = {}
        fila_listagem = []
        tabela = {'simbolos':tabela_simbolos, 'ext':tabela_ext, 'ent':tabela_ent, 'overlay': overlay_table}

        for string_linha in codigo:
            next_endr_linha, found_overlay  = self.analisar_linha1(string_linha,\
                                                    endr_linha, fila_listagem, tabela)

            if next_endr_linha == False:
                continue
            else:
                endr_linha = next_endr_linha


        print(tabela_simbolos)
        return (tabela_simbolos, tabela_ent, tabela_ext, fila_listagem), overlay_table

    def criar_linha_montagem(self, endr, endr_end, endr_rel, instru, op, op_rel):
        """ Cria uma linha com os dados recebidos e acrescenta dados para a montagem. """
        global INSTRUCOES 
        # 	00 0a 0xxx bb
        # 	01 0a 0xxx bbbbbb
        size = endr_end - endr
        tipo = 0 if size == 1 else 1
        nibble_rel = 2*endr_rel + op_rel
        if tipo == 0:
            return [tipo, nibble_rel, endr, op]
        else:
            op = op if op else 0
            instru = INSTRUCOES[instru]
            print( tipo, nibble_rel, endr, hex((instru << 16) + op) )
            return [tipo, nibble_rel, endr, (instru << 16) + op]

    def segundo_passo(self, tabela_simbolos, tabela_ent, tabela_ext, fila_listagem):
        """ Processa uma fila de listagem e cria uma fila de montagem. """
        global OP_ABS_INSTRUCOES

        print("/"*50,f"\n// Segundo passo\n")

        fila_montagem = []

        # Extrair primeiro e ultimo endereço
        FIRST_ENDR = fila_listagem[0][0]
        LAST_ENDR = fila_listagem[-1][1]

        for tokens in fila_listagem:
            # Recebe tokens
            print(tokens, end=' -> ')
            endr, endr_end, endr_rel, label, instru, op = tokens

            endr_rel = op_rel = True

            # Resolve labels no operando
            if op in tabela_simbolos:
                op, op_rel = self.solve_label(tabela_simbolos, op)

            # Resolve relocabilidade do operando
            if instru in OP_ABS_INSTRUCOES:
                op_rel = False

            # Monta fila de montagem
            linha_montagem = self.criar_linha_montagem(endr, endr_end, endr_rel, instru, op, op_rel)

            fila_montagem.append(linha_montagem)

        return fila_montagem, (FIRST_ENDR, LAST_ENDR)

    def format_bytes(self, tipo, nibble_rel, endr, value, loader=False):
        """ Formata os parâmetros segundo especificação do loader. """
        if loader and tipo == 0:
            return f"{endr:04X}{value:02X}"
        elif loader and tipo == 1:
            b2 = value >> 16
            b1 = (value & 0xFFFF) >> 8
            b0 = (value & 0xFF)
            print("formatting", b2, b1, b0)
            return f"{endr:04X}{b2:02X}{endr+1:04X}{b1:02X}{endr+2:04X}{b0:02X}"
        elif tipo == 0:
            return f"{tipo:02X}{nibble_rel:02X}{endr:04X}{value:02X}"
        elif tipo == 1:
            return f"{tipo:02X}{nibble_rel:02X}{endr:04X}{value:06X}"

    def montagem_absoluta(self, fila_montagem, ENDR_LIMITES):
        """ Cria um arquivo .hex carregável pelo loader. """
        code_hex = ''
        for linha in fila_montagem:
            s = self.format_bytes(*linha)
            code_hex += s

        FIRST_ENDR, LAST_ENDR = ENDR_LIMITES
        code_hex += f'FF{FIRST_ENDR:04X}'
        return code_hex


    def montagem_relocavel(self):
        """ Cria um arquivo .robj carregável pelo linker. """
        pass

    def montagem_loader(self, fila_montagem):
        """ Cria um arquivo .hex carregável pela MVN. """
        code_hex = ''
        for linha in fila_montagem:
            s = self.format_bytes(*linha,loader=True)
            code_hex += s
        return code_hex

    def write_hex(self, filepath, code_hex):
        with open(f'{filepath}.hex',"w+") as s:
            s.write(code_hex)

    def montar(self, filepath, tipo='absoluta'):
        f = open(f'{filepath}.asm', "r+")
        print(f"\n====== Montando {filepath} ======")

        if tipo == 'loader':
            p1, overlays = self.primeiro_passo(f)
            fila_montagem, ENDR_LIMITES = self.segundo_passo(*p1)
            code_hex = self.montagem_loader(fila_montagem)
            print(code_hex)
            self.write_hex(filepath, code_hex)

        elif tipo == 'absoluta':
            p1, overlays = self.primeiro_passo(f)
            fila_montagem, ENDR_LIMITES = self.segundo_passo(*p1)
            code_hex = self.montagem_absoluta(fila_montagem, ENDR_LIMITES)
            print(code_hex)
            self.write_hex(filepath, code_hex)


m = Montador()
m.montar('loader', 'loader')
m.montar('print100')
m.montar('teste_overlay1')
