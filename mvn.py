##############################
#
# Simulador de Maquina de Von Neuman
#
##############################

from motordeeventos import MotorDeEventos, Evento

#================
# CONSTANTES
#================
MEM_SIZE = 4096 # Bytes
HD_SIZE = 2**15 
MEM_POS_SIZE = 1 # Bytes
WORD_SIZE = 1 # Bytes
MAX_BITS = 2**(WORD_SIZE*8)
LONG_SIZE = 2 # Bytes

#================
# Simulador
#================
class Simulador():
    def __init__(self):
        self.CI = 0
        self.AC = 0
        self.state = 0
        self.MEM = bytearray(MEM_SIZE)
        self.HD = bytearray(HD_SIZE)
        self.INSTRUCOES = {
            0:self.JP, 1:self.JZ, 2:self.JN, 3:self.LV, 4:self.PLUS,
            5:self.MINUS, 6:self.MULT, 7:self.DIV, 8:self.LD, 9:self.MM, 0xA:self.SC, 0xB:self.RS,
            0xC:self.HM, 0xD:self.GD, 0xE:self.PD, 0xF:self.OS, 0x10:self.SHIFT_RIGHT, 0x11:self.SHIFT_LEFT,
            0x13:self.CP, 0x14:self.JPE, 0x15:self.JPNE
        }
        self.REV_INSTRU = ['JP','JZ','JN','LV','+','-','*','/','LD','MM','SC','RS','HM','GD','PD','OS','>>','<<','&&','CP','JPE','JPNE']
        self.OP_ABS_INSTRUCOES = [3, 0xF, 0x13, 0x10, 0x11]
        #/////////////////
        #// Sistema operacional
        self.sistop = None

        #/////////////////
        #// Registers
        self.reg_offset = 0
        self.reg_comparison = 0

        #/////////////////
        #// Adm de Memória
        self.relocate = False
        self.overlays = {}

        #/////////////////
        #// Buffer
        self.buffer = ""
        self.buffer_len = 0
        self.buffer_CI = 0

        self.load_loader()

    #=====================
    # Utils
    #=====================
    def readPointer(self, endr):
        return ( self.MEM[endr] << 8 ) + self.MEM[endr + 1] 

    def readByte(self,op):
        return self.MEM[op]

    def deleteBytes(self, endr, n):
        self.MEM[endr:endr+n] = [0 for i in range(n)]

    def storeByte(self,op, b=None):
        if b == None:
            self.MEM[op] = self.AC
        else:
            self.MEM[op] = b

    def storeWord(self,op, word):
        self.storeByte(op, word >> 8)
        self.storeByte(op, word & 0xFF)

    def peek_buffer(self, n):
        b = self.buffer[self.buffer_CI:self.buffer_CI+n]
        return b

    def read_buffer(self, n):
        b = int(self.buffer[self.buffer_CI:self.buffer_CI+n], 16)
        self.buffer_CI += n
        return b

    def buffer_back(self, n):
        self.buffer_CI -= n
        b = int(self.buffer[self.buffer_CI:self.buffer_CI+n], 16)
        return b

    def updateCI(self, op=None):
        if op == None:
            self.CI += 3
        else:
            self.CI = op

    #=====================
    # Instruções
    #=====================
    def JP(self,op): #op = 12 bits
        if op == 0:
            self.state = 0
        self.updateCI(op)

    def JZ(self,op): #op = 12 bits
        if self.AC == 0:
            self.updateCI(op)
        else:
            self.updateCI()

    def JN(self,op): #op = 12 bits
        if self.AC >= 0x80:
            self.updateCI(op)
        else:
            self.updateCI()

    def LV(self,op): #op = 8 bits
        self.AC = op
        self.updateCI()

    def PLUS(self,op): #op = 12 bits
        self.AC = (self.AC + self.readByte(op))%256 
        self.updateCI()

    def MINUS(self,op): #op = 12 bits
        self.AC = (self.AC - self.readByte(op))%256 
        self.updateCI()

    def MULT(self,op):  #op = 12 bits
        self.AC = (self.AC * self.readByte(op))%256
        self.updateCI()

    def DIV(self,op): #op = 12 bits
        self.AC = int(self.AC // self.readByte(op))%256
        self.updateCI()

    def LD(self,op): #op = 12 bits
        self.AC = self.readByte(op)
        self.updateCI()

    def MM(self,op): #op = 12 bits
        self.storeByte(op,self.AC)
        self.updateCI()

    def SC(self,op): #op = 12 bits
        """ Subroutine Call """
        val = self.CI+3
        self.storeByte(op, 0)
        self.storeByte(op+1, val >> 8)
        self.storeByte(op+2, val & 0xFF)
        self.updateCI(op+3)

    def RS(self,op): #op = 12 bits
        """ Return Subroutine """
        self.updateCI(op)

    def HM(self,op): #op = 12 bits
        print("----------------HALTED")
        self.state = 0
        self.updateCI(op)

    def GD(self,op):
        temp = self.read_buffer(2)
        self.AC = temp
        self.updateCI()

    def PD(self,op):
        print(f'PD {self.AC} hex:{self.AC:02X}')
        self.updateCI()

    def OS(self, op):
        if op == 3:
            # Chama monitor de overlay
            # Lê os prox 2 bytes
            self.sistop.monitor_de_overlay()
            self.updateCI(self.CI+6)
        elif op == 6:
            self.sistop.loader()

    def CP(self, op):
        if self.AC == op:
            self.reg_comparison = 1
        else:
            self.reg_comparison = 0
        self.updateCI()

    def JPE(self, op):
        """ Jump if Equal """
        if self.reg_comparison:
            self.updateCI(op)
        else:
            self.updateCI()

    def JPNE(self, op):
        """ Jump if Not Equal """
        if not self.reg_comparison:
            self.updateCI(op)
        else:
            self.updateCI()

    def SHIFT_RIGHT(self,op):
        self.AC = (self.AC >> op)%256
        self.updateCI()

    def SHIFT_LEFT(self,op):
        self.AC = (self.AC << op)%256
        self.updateCI()

    #=====================
    # Funções Loader
    #=====================

    def load_loader(self):
        f = open("loader.hex", "r+").read().strip()
        n = len(f)-6
        i = 0
        while i < n:
            endr = int(f[i:i+4],16)
            byte = int(f[i+4:i+6],16)
            #print(endr, byte)
            self.MEM[endr] = byte
            i += 6

    def extrai_tamanho(self):
        return self.buffer_len - self.buffer_CI

    def load_buffer(self, filepath):
        f = open(filepath, "r+").read().strip()
        self.buffer = f
        self.buffer_CI = 0
        self.buffer_len = len(f)

    #===========================
    # Funções execução
    #===========================

    def tratar(self, instru, op):
        func = self.INSTRUCOES[instru]

        # Transforma o endereço virtual para real
        if not instru in self.OP_ABS_INSTRUCOES:
            #newop = self.sistop.do_page_table(op)
            newop = self.sistop.mem_acessar(op)
        else:
            newop = op

        func(newop)


    def getNextInstruction(self):
        """ Faz um desassembly da instrução apontada por CI. """
        instru = self.MEM[self.CI]
        op = (self.MEM[self.CI+1] << 8) + self.MEM[self.CI+2]
        return instru, op

    def run_step(self):
        """ Executa a instrução atual apontada por CI. """
        if self.state == 1:
            instru, op = self.getNextInstruction()
            print(f"  RUNNING at {self.CI:04X}",f'{self.REV_INSTRU[instru]}({instru})', f'{op:04X}', f'[AC:{self.AC}]',end='\n')
            self.tratar(instru, op)

    def run(self, filepath):
        """ Carrega um arquivo na MVN e o roda. """
        self.load(filepath)
        # Aponta para o endereço inicial
        self.CI = self.sistop.get_ini_pointer()
        self.state = 1
        print(f"===============Running {filepath}")
        while self.state == 1:
            self.run_step()

    #======================= 
    # Funções Utils
    #======================= 
    def dump(self, endr_ini=0, endr_end=0xFFF):
        """ Retorna o conteúdo formatado da memória RAM de endr_ini a endr_end. """
        print_ini = endr_ini&0xFF0
        print_end = endr_end|0xF
        b = self.MEM[print_ini:print_end+1]
        n = len(b)//16
        print_string = "   0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F\n"
        for k in range(n):
            print_string += f"{(print_ini >> 4)+k:02X} "
            print_string += ' '.join(f"{byte:02X}" for byte in b[k*16:k*16+16])
            print_string += '\n'
        return print_string

print("INICIANDO MVN")
#s = Simulador()
#s.run('teste_overlay1.hex')