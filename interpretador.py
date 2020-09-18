from motordeeventos import MotorDeEventos, Evento
from tabelatrans import TabelaTransicaoTratamento
import sys
import re
class Classificador(MotorDeEventos):
    def __init__(self, arquivo_leitura, regras):
        super(Classificador, self).__init__("C")
        # Setup
        self.entrada = list(open(arquivo_leitura,"r+").read())
        self.indexChar = 0
        self.indexLinha = 0
        self.entrada.append("\n")
        self.entrada.append("EOF")
        self.indexLinhas = self.getIndexLinhas()
        self.EOF = False
        self.word = ""

        # Regras dict {"especial","numero","identificador","palavra-chave"}
        self.regras = regras

    def goto(self, linha):
        self.indexLinha = linha
        self.indexChar = self.indexLinhas.index(linha)

    def getIndexLinhas(self):
        count = 0
        lista = []
        for i in self.entrada:
            lista.append(count)
            if i == "\n":
                count += 1
        return lista

    def chartype(self, char):
        if char in self.regras["especial"]:
            return 0
        elif char == " " or char == "\t":
            return 1
        elif char == "\n":
            return 2
        else: # Alfanumerico
            return 3

    def get_char(self):
        char = self.entrada[self.indexChar]
        self.indexLinha = self.indexLinhas[self.indexChar]
        self.indexChar += 1
        if char == "EOF":
            self.EOF = True
            return char
        else:
            return char

    def classify(self, char=None, word=None):
        if char and char in self.regras["especial"]:
            return "especial"
        elif word and re.match(self.regras["numero"], word):
            return "numero"
        elif word and word in self.regras["palavrachave"]:
            return "palavrachave"
        elif word and re.match(self.regras["identificador"], word):
            return "identificador"
        return None

    def run(self):
        linebuffer = ""
        char = self.get_char()
        if self.EOF:
            return 0

        chartype = self.chartype(char) 
        linebuffer += char

        # Sinaliza transição entre sequencias alfanumericas
        if chartype == 0:
            # Classifica e envia ao Reconhecedor caso haja classificação valida
            token_class = self.classify(char=char)
            self.output("R", Evento(self, token_class, char))
            self.word = ""
        elif chartype < 3 and self.word != "": 
            # Classifica e envia ao Reconhecedor caso haja classificação valida
            token_class = self.classify(word=self.word)
            if token_class == "numero":
                self.output("R", Evento(self, token_class, int(self.word)))
            elif token_class:
                self.output("R", Evento(self, token_class, self.word))
            # Limpa a palavra
            self.word = ""

        # Sinaliza caracter não whitespace
        elif chartype == 3: 
            # Classifica e envia ao Reconhecedor caso haja classificação valida
            token_class = self.classify(char=char)
            if token_class:
                self.output("R", Evento(self, token_class, char))
            # Adiciona o char a palavra
            self.word += char

        # Transição entre linhas
        if chartype == 2: 
            #print(linebuffer,end="")
            linebuffer = ""

        return 1

class Reconhecedor(MotorDeEventos):

    def __init__(self, regras):
        super(Reconhecedor, self).__init__("R")
        self.tt = TabelaTransicaoTratamento(regras)
        self.state = self.tt.ini

    def run(self):
        ev = self.getNextEvento()
        if not ev:
            return 0

        # Acha o proximo estado, dados os parametros da transição
        state_ini = self.state
        self.state, _ = self.tt.transicao(self.state, ev.tipo, ev.dados)
        if not self.state:
            self.state, _ = self.tt.transicao(self.tt.ini, ev.tipo, ev.dados)

        #print("R",self.state,ev.tipo,ev.dados)
        # Envia os dados da transição para o Decisor
        dados = [state_ini, ev.tipo, ev.dados]
        self.output("D", Evento(self, self.state, dados))

        return 1

class Decisor(MotorDeEventos):
    def __init__(self, tabela_tratamento):
        super(Decisor, self).__init__("D")
        self.tt = tabela_tratamento
        self.complementos = {}

    def run(self):
        ev = self.getNextEvento()

        if not ev:
            return 0

        # Atualiza os complementos da rotina de tratamento
        state_ini = ev.dados[0]
        if ev.tipo in self.complementos:
            self.complementos[ev.tipo] += ev.dados[1:]
        else:
            self.complementos.update({ev.tipo:ev.dados[1:]})

        # Encontra a rotina
        next_state, rot_tratamento = self.tt.transicao(*ev.dados)

        # Se rotina foi encontrada envia para tratamento
        if rot_tratamento:
            self.output("T",Evento(self,"executar",(rot_tratamento, self.complementos)))
            self.complementos = {}
        
        return 1

class Tratamento(MotorDeEventos):
    def __init__(self, rotinas, rotina_label):
        super(Tratamento, self).__init__("T")
        self.rotinas = rotinas
        self.JUMPING = False
        self.rotina_label = rotina_label

    def jump(self, label):
        self.JUMPING = True
        #print("hey")

    def run(self):
        ev = self.getNextEvento()

        if not ev:
            return 0
        # Trata os eventos com a rotina adequada
        rot_tratamento, complementos = ev.dados

        if self.JUMPING:
            #print("Pulando", *ev.dados)
            isLabel = False
            if rot_tratamento == self.rotina_label:
                isLabel = self.rotinas[rot_tratamento](complementos)
            if isLabel:
                self.JUMPING = False
        else:
            #print("Executar", *ev.dados)
            self.rotinas[rot_tratamento](complementos)

        return 1
    

class Interpretador(MotorDeEventos):
    def __init__(self, C_args, R_args, T_args):
        super(Interpretador, self).__init__("Interpretador")
        self.C = Classificador(*C_args)
        self.R = Reconhecedor(*R_args)
        self.tabela_transicao = self.R.tt
        #for i in self.tabela_transicao.rules:
            #print(i, self.tabela_transicao.rules[i])
        self.D = Decisor(self.tabela_transicao)
        self.T = Tratamento(*T_args)
        
        # Links
        self.C.linkarMotor([],[self.R])
        self.D.linkarMotor([self.R],[self.T])

