##############################
#
# LINKER-RELOCADOR
#
##############################

from motordeeventos import MotorDeEventos, Evento
from overlay import MonitorDeOverlay

#================
# CONSTANTES
#================
MEM_SIZE = 4096 # Bytes
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
        self.INSTRUCOES = {
            "JP":self.JP, "JZ":self.JZ, "JN":self.JN, "LV":self.LV, "+":self.PLUS,
            "-":self.MINUS, "*":self.MULT, "LD":self.LD, "MM":self.MM, "SC":self.SC, "RS":self.RS,
            "HM":self.HM, "GD":self.GD, "PD":self.PD, "OS":self.OS
        }

        self.relocate = False
        self.offset = 0

        self.overlays = {}

        self.buffer = ""
        self.buffer_CI = 0

        self.load_loader()

    #=====================
    # Utils
    #=====================
    def readByte(op):
        return self.MEM[op]

    def storeByte(op, b=None):
        if b == None:
            self.MEM[op+self.offset] = self.AC
        else:
            self.MEM[op+self.offset] = b

    def storeWord(op, word):
        self.storeByte(op, word >> 8)
        self.storeByte(op, word & 0xFF)

    def updateCI(self, op=None):
        if op == None:
            self.CI += 2
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
        self.storeWord(op,self.CI+2)
        self.updateCI(op+2)

    def RS(self,op): #op = 12 bits
        self.updateCI(op)

    def HM(self,op): #op = 12 bits
        print("----------------HALTED")
        self.state = 0
        self.updateCI(op)

    def GD(self):
        temp = self.buffer[self.buffer_CI:self.buffer_CI+2]
        try:
            self.AC = int(self.buffer[self.buffer_CI:self.buffer_CI+2],16)
        except:
            pass
        self.buffer_CI += 2
        self.updateCI()

    def PD(self):
        print(hex(self.AC))
        self.updateCI()

    def OS(self, op):
        if op == 0:
            self.relocate = False
        elif op == 1:
            self.relocate = True
        elif op == 3:
            a = self.AC & 0xF
            if a >= 2:
                self.AC = 0
            else:
                self.AC = 1
        elif op == 4:
            a = self.AC & 0xF
            if a % 2 == 0:
                self.AC = 0
            else:
                self.AC = 1
        elif op & 0xF00 == 0x100:
            # Extrai o carry out da soma de 1 byte
            op1 = op & 0xFF
            soma = self.AC + self.readByte(op1)
            msb = soma >> 8
            self.AC = msb
        elif op == 0xF00:
            self.AC = (self.AC >> 4) & 0xFF
        elif op == 0xF01:
            self.AC = (self.AC << 4) & 0xFF
        self.updateCI()

    #=====================
    # Funções 
    #=====================

    def load_loader(self):
        f = open("loader.hex", "r+").read().strip()
        n = len(f)-6
        i = 0
        while i < n:
            endr = int(f[i:i+4],16)
            byte = int(f[i+4:i+6],16)
            print(endr, byte)
            self.MEM[endr] = byte
            i += 6

    def extrai_tamanho(self):
        return len(self.buffer)

    def load(self, filepath):
        self.CI = 4
        f = open(filepath, "r+").read().strip()
        self.buffer = f
        self.buffer_CI = 0

    def monitor_de_overlay(self, n):
        # Carrega o overlay
        self.load(f"overlay{n}.hex")
        # Extrai o tamanho
        self.offset = self.extrai_tamanho(self.buffer)
        # Ponteiro para o final do último bloco
        b1 = self.readByte(2)
        b0 = self.readByte(3)
        # Calculo da nova posição do ponteiro
        endr = (b1 << 8 + b0) + offset
        # Guardamos a nova palavra
        self.storeWord(2, endr)
        # Coloca o contador de instruções para o início do loader
        self.CI = 4


    def tratar(self, instru, op):
        self.INSTRUCOES[instru](op)

    def dump(self, endr_ini=0, endr_end=0xFFF):
        pass

    def run(self, filepath):
        self.load(filepath)

        return
        if self.state == 1:
            instru, op = self.getNextInstruction()
            self.tratar(instru, op)

#s = Simulador()
#print(s.MEM[:50])
print("INICIANDO MVN")
print(0)
print(16)