from motordeeventos import MotorDeEventos, Evento
from interpretador import Interpretador

import sys
import os

# Determina o arquivo a ser lido
n = len(sys.argv)
arquivo_leitura = "./script.ts"
if n == 2:
    arquivo_leitura = f"./{sys.argv[1]}"

class Linguagem(Interpretador):
    def __init__(self, arquivo_leitura, infile, outfile):
        #===========================
        # Argumentos Classificador
        #===========================
        C_arquivo_leitura = arquivo_leitura
        C_palavras_chaves = ["LET","READ","GOTO","IF","WRITE"]
        C_regras ={"especial":[":","=","+","-","*","/",";","<",">"],
                "numero":"\A(\d+)",
                "identificador":"(\w+)",
                "palavrachave": C_palavras_chaves
        }
        C_args = (C_arquivo_leitura, C_regras)

        #===========================
        # Argumentos Reconhecedor
        #===========================
        # Tabela Transição e Tratamento
        R_regras = '''
        >1{p:LET 2}
        2{i:% 3}
        3{e:= 4 func_let_store}
        4{i:% 5;n:% 5}
        5{e:+ 4;e:- 4;e:* 4;e:/ 4}
        5{e:; 1 func_let_calc}
        1{p:READ 6}
        6{i:% 7 func_read}
        1{p:GOTO 8}
        8{i:% 9}
        9{p:IF 10 func_goto_store;e:; 1 func_goto}
        10{i:% 11;n:% 11}
        11{e:+ 10;e:- 10;e:* 10;e:/ 10}
        11{e:= 12;e:> 12;e:< 12}
        12{i:% 13;n:% 13}
        13{e:+ 12;e:- 12;e:* 12;e:/ 12}
        13{e:; 1 func_if_calc}
        1{i:% 14;n:% 14}
        14{e:: 1 func_label}
        1{p:WRITE 15 func_write}
        15{i:% 5;n:% 5}
        '''
        R_args = [R_regras]
        #===========================
        # Argumentos Tratamentos 
        #===========================
        self.rotinas = {func_name:getattr(self, func_name) for func_name in dir(self) if "func" in func_name }
        T_args = [self.rotinas, "func_label"]

        super(Linguagem, self).__init__(C_args,R_args,T_args)

        #==========================
        # Flags
        #==========================
        self.WRITE = False
        self.JUMPING = False

        #==========================
        # Área da Linguagem
        #==========================
        self.vars = {}
        self.reg = None
        self.labels = {}
        self.infile = None
        self.outfile = None
        if infile:
            self.set_infile(infile)
        if outfile:
            self.set_outfile(outfile)

    def set_infile(self, infile):
        #print(f"\n\nlendo {infile}\n\n")
        self.infile = open(infile,"r").read().strip().split(' ')

    def set_outfile(self, outfile):
        self.outfile = outfile
        with open(self.outfile,"w+") as f:
            f.write("")

    def run(self):
        print("==========\nEXECUTANDO LINGUAGEM ALTO NÍVEL\n===========")
        count = 1
        while count != 0:
            count = 0
            count += self.C.run()
            count += self.R.run()
            count += self.D.run()
            count += self.T.run()
        print("==========FIM ===========")
    
    def reset_flags(self):
        self.WRITE = False
        self.JUMPING = False

    def func_next(self, complementos):
        pass

    def func_write(self, complementos):
        self.WRITE = True

    def func_read(self, complementos):
        var_name = complementos[7][1]
        self.vars[var_name] = self.infile.pop(0)

    def func_let_store(self, complementos):
        """ Armazena o id coletado na transição do estado 2 ao 3 e o coloca
        no registrador. Caso o id não exista, é criado uma entrada na tabela 
        de variáveis.
        """
        var_name = complementos[3][1]
        self.reg = var_name
        if not var_name in self.vars:
            self.vars[var_name] = None
        return 0

    def func_getvalue(self, tipo, value):
        # Substitui as variáveis por seus valores
        if tipo == "identificador":
            var_name = value
            try:
                value = self.vars[var_name]
            except:
                raise Exception(f"Nome de variável '{var_name}' não existe")
        return f"{value}"

    def func_calc(self, a, b):
        """ Recebe uma lista de operandos e uma lista de operações
        e resolve o cálculo. a = operandos, b = operações.
        """
        t = len(a+b)
        queue = [0] * t
        queue[0::4] = a[0::2]
        queue[1::4] = a[1::2]
        if t > 2:
            queue[2::4] = b[0::2]
            queue[3::4] = b[1::2]

        # Constrói string
        string = ""
        for k in range(0,t,2):
            tipo = queue[k]
            val = queue[k+1]
            value = self.func_getvalue(tipo, val)
            string += f"{value} "
        
        # Evalua o resultado
        result = eval(string)
        return result

    def func_let_calc(self, complementos):
        """ Resolve a expressão aritmética e substitui o valor das variáveis se estas
        já existirem. O resultado da expressão aritmética é atribuído à variável que
        estiver no registrador. Caso seja um WRITE, este resultado é escrito no arquivo outfile.
        """
        # Assign de um número com operações
        a = complementos[5]
        b = [] if not 4 in complementos else complementos[4]

        result = self.func_calc(a,b)

        if self.WRITE:
            with open(self.outfile, "a+") as f:
                f.write(f"{result}\n")
        else:
            self.vars[self.reg] = result
        self.reg = None
        self.reset_flags()
        return 0

    def func_label(self, complementos):
        label = complementos[14][1]
        if not label in self.labels:
            self.labels.update({label:self.C.indexLinha})

        # Se a label for a designada, paramos o jump
        if label == self.JUMPING:
            self.JUMPING = False
            return True
        else:
            return False

    def func_goto_label(self, label):
        if label in self.labels:
            linha = self.labels[label]
            self.C.goto(linha)
        else:
            self.JUMPING = label
            self.T.jump(label)

    def func_goto(self, complementos):
        linha = self.labels[complementos[9][1]]
        self.C.goto(linha)

    def func_goto_store(self, complementos):
        self.reg = complementos[9][1]

    def func_if_calc(self, complementos):
        # Condição
        tipo = complementos[12].pop(0)
        cond = complementos[12].pop(0)
        cond = "==" if cond == "=" else cond
        # Operandos
        a = complementos[11]
        c = complementos[13]
        # Operações
        b = [] if not 10 in complementos else complementos[10]
        d = [] if not 12 in complementos else complementos[12]

        # Calcula os resultados parciais
        result1 = self.func_calc(a,b)
        result2 = self.func_calc(c,d)
        ifstring = f"{result1} {cond} {result2}"

        if eval(ifstring):
            self.func_goto_label(self.reg)
            self.reg = None
        else:
            return 0
