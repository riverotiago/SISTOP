from motordeeventos import MotorDeEventos, Evento
from interpretador import Interpretador
from linguagem import Linguagem
from montador import Montador
from simulador import Simulador
import sys
import os

"""
Inicia operação $JOB nome Login - inicia um novo job, reinicia todo o sistema
Escolhe pasta $DISK pasta Simula disco do sistema nesta pasta do hospedeiro
Arquivos existentes $DIRECTORY Lista o conteúdo da pasta do hospedeiro
Cria arquivo $CREATE nome Cria no disco um novo arquivo, se ainda não existir
Apaga arquivo $DELETE nome Remove do disco o arquivo indicado, se existir
Mostra conteúdo $LIST nome Apresenta o conteúdo do arquivo indicado, se existir
Mídia de entrada $INFILE nome Adota o arquivo indicado como a fita de entrada
Mídia de saída $OUTFILE nome Adota o arquivo indicado como a fita de saída
Arquivo em disco $DISKFILE nome Adota o arquivo indicado como arquivo em disco
Executa programa $RUN nome Executa o programa indicado (de sistema ou ususário)
Encerra operação $ENDJOB nome Finaliza pendências e termina o job corrente
"""

# Determina o arquivo a ser lido
n = len(sys.argv)
arquivo_leitura = "./script.cl"
if n == 2:
    arquivo_leitura = f"./{sys.argv[1]}"

class Controle(Interpretador):
    def __init__(self, arquivo_leitura):
        #===========================
        # Argumentos Classificador
        #===========================
        C_arquivo_leitura = arquivo_leitura
        C_palavras_chaves = ["JOB","DISK","DIRECTORY",
                "CREATE","DELETE","LIST","INFILE","OUTFILE",
                "DISKFILE","RUN","ENDJOB"]
        C_regras ={"especial":["$"],
                "numero":"\A(\d+)",
                "identificador":"([a-zA-Z][a-zA-Z0-9\.]*)",
                "palavrachave": C_palavras_chaves
        }
        C_args = (C_arquivo_leitura, C_regras)

        #===========================
        # Argumentos Reconhecedor
        #===========================
        # Tabela Transição e Tratamento
        R_regras = '''
        >1{e:$ 2}
        2{p:JOB 3}
        3{i:% 4 func_job}
        2{p:DISK 5}
        5{i:% 6 func_disk}
        2{p:DIRECTORY 7 func_directory}
        2{p:CREATE 8}
        8{i:% 9 func_create}
        2{p:DELETE 10}
        10{i:% 11 func_delete}
        2{p:LIST 12}
        12{i:% 13 func_list}
        2{p:INFILE 14}
        14{i:% 15 func_infile}
        2{p:OUTFILE 16}
        16{i:% 17 func_outfile}
        2{p:DISKFILE 18}
        18{i:% 19 func_diskfile}
        2{p:RUN 20}
        20{i:% 21 func_run}
        2{p:ENDJOB 22}
        22{i:% 23 func_endjob}
        '''
        R_args = [R_regras]
        #===========================
        # Argumentos Tratamentos 
        #===========================
        self.rotinas = {func_name:getattr(self, func_name) for func_name in dir(self) if "func" in func_name }

        T_args = [self.rotinas, None]

        super(Controle, self).__init__(C_args,R_args,T_args)
        #print(self.R.tt.rules)

        #==========================
        # Área do Controle
        #==========================
        self.interp_linguagem = None
        self.disk = None
        self.infile = None
        self.outfile = None
        self.job = None
        self.montador = Montador()
        self.simulador = Simulador()

    def run(self):
        count = 1
        while count != 0:
            count = 0
            count += self.C.run()
            count += self.R.run()
            count += self.D.run()
            count += self.T.run()
        print("FIM =======")

    def func_job(self,complementos):
        nome_job = complementos[4][1]
        self.disk = None
        self.infile = None
        self.outfile = None
        self.job = nome_job

    def func_disk(self,complementos):
        pasta= complementos[6][1]
        path = f"./{pasta}/"
        self.disk = path
        if not os.path.exists(path):
            os.makedirs(path)

    def func_directory(self,complementos):
        for i in os.listdir(self.disk):
            print(i)

    def func_create(self,complementos):
        nome = complementos[9][1]
        path = f"{self.disk}/{nome}"
        open(path,"w+").close()

    def func_delete(self,complementos):
        nome = complementos[11][1]
        path = f"{self.disk}/{nome}"
        if os.path.exists(path):
            os.remove(path)

    def func_list(self,complementos):
        nome = complementos[13][1]
        path = f"{self.disk}/{nome}"
        with open(path,"r+") as f:
            for line in f:
                print(line, end="")
        print("")
            
    def func_infile(self,complementos):
        nome = complementos[15][1]
        self.infile = nome

    def func_outfile(self,complementos):
        nome = complementos[17][1]
        self.outfile = nome

    def func_diskfile(self,complementos):
        pass

    def func_run(self,complementos):
        nome = complementos[21][1]
        if nome == "montador":
            self.montador.run(self.disk+self.infile,self.disk+self.outfile)
        elif nome == "ligador":
            pass
        elif nome == "simulador":
            self.simulador.run()
            self.simulador.dump()
        elif nome == "loader":
            self.simulador.load(self.disk+self.infile)
        else:
            file = f"{nome}"
            inf = "" if not self.infile else self.disk+self.infile
            outf = "" if not self.outfile else self.disk+self.outfile
            self.interp_linguagem = Linguagem(self.disk+file, inf, outf)
            self.interp_linguagem.run()


    def func_endjob(self,complementos):
        print(self.disk, self.infile, self.outfile, self.job)
    
control = Controle(arquivo_leitura)
control.run()