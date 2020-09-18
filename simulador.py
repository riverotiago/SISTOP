MEM_SIZE = 4096 # Bytes
MEM_POS_SIZE = 1 # Bytes
WORD_SIZE = 1 # Bytes
MAX_BITS = 2**(WORD_SIZE*8)
LONG_SIZE = 2 # Bytes

class MVN():
    def __init__(self):
        self.CI = 0 #Program Counter
        self.AC = 0 #Acumulador
        self.MEM = bytearray(MEM_SIZE)
        self.buffer = ""
        self.buffer_CI = 0
        self.INS = {}
        self.INS_NAMES = {}
        self.state = 0

        self.mapInstructions()

    #--------------------
    # Funções elementares
    #--------------------
    def readInstructionOp(self,pos):
        # Extrai a instrução e operando
        instruction = self.MEM[pos] >> 4 # Pega os primeiros 4 bits
        op = ((self.MEM[pos] & 0x0F) << 8) + self.MEM[pos+1] # Pega os próximos 12 bits
        return instruction,op

    def readByte(self,pos):
        return self.MEM[pos]

    def storeByte(self,pos,value):
        self.MEM[pos] = value

    def storeWord(self,pos,word):
        self.MEM[pos] = word >> 8
        self.MEM[pos+1] = (word & 0x00FF) 

    def nextInstruction(self,pos=None):
        if not pos:
            self.CI += 2
        else:
            self.CI = pos

    #-------------------
    # Instruções 
    #-------------------
    def JP(self,op): #op = 12 bits
        self.nextInstruction(op)

    def JZ(self,op): #op = 12 bits
        if self.AC == 0:
            self.nextInstruction(op)
        else:
            self.nextInstruction()

    def JN(self,op): #op = 12 bits
        if self.AC >= 0x80:
            self.nextInstruction(op)
        else:
            self.nextInstruction()

    def LV(self,op): #op = 8 bits
        self.AC = op
        self.nextInstruction()

    def PLUS(self,op): #op = 12 bits
        self.AC = (self.AC + self.readByte(op))%256 
        self.nextInstruction()

    def MINUS(self,op): #op = 12 bits
        self.AC = (self.AC - self.readByte(op))%256 
        self.nextInstruction()

    def MULT(self,op):  #op = 12 bits
        self.AC = (self.AC * self.readByte(op))%256
        self.nextInstruction()

    def DIV(self,op): #op = 12 bits
        self.AC = int(self.AC / self.readByte(op))%256
        self.nextInstruction()

    def LD(self,op): #op = 12 bits
        self.AC = self.readByte(op)
        self.nextInstruction()

    def MM(self,op): #op = 12 bits
        self.storeByte(op,self.AC)
        self.nextInstruction()

    def SC(self,op): #op = 12 bits
        self.storeWord(op,self.CI+2)
        #print("subroutine",hex(op),hex(self.CI+2),hex(self.MEM[op]),hex(self.MEM[op+1]))
        self.nextInstruction(op+2)

    def RS(self,op): #op = 12 bits
        #print("returning to",op)
        self.nextInstruction(op)

    def HM(self,op): #op = 12 bits
        print("----------------HALTED")
        self.state = 0
        self.nextInstruction(op)

    def GD(self):
        temp = self.buffer[self.buffer_CI:self.buffer_CI+2]
        try:
            self.AC = int(self.buffer[self.buffer_CI:self.buffer_CI+2],16)
        except:
            pass
        self.buffer_CI += 2
        self.nextInstruction()

    def PD(self):
        print(hex(self.AC))
        self.nextInstruction()

    def SO(self):
        self.nextInstruction()

    #-------------------
    # Atributos 
    #-------------------
    def mapInstructions(self):
        instructions = [self.JP,self.JZ,self.JN,self.LV,self.PLUS,
        self.MINUS,self.MULT,self.DIV,self.LD,self.MM,self.SC,self.RS,
        self.HM,self.GD,self.PD,self.SO]

        self.INS = {k:instructions[k] for k in range(len(instructions))}
        self.INS_NAMES = {k:instructions[k].__name__ for k in range(len(instructions))}

    def hasOp(self,instruction):
        if instruction < 13:
            return True
        else:
            return False

    #-------------------
    # Execução
    #-------------------
    def execute_step(self):
        # Executa a instrução atual
        instruction, op = self.readInstructionOp(self.CI)

        if self.hasOp(instruction):
            self.INS[instruction](op)

        else:
            self.INS[instruction]()

class Simulador():
    def __init__(self):
        # Programa deve começar a partir de @ 100
        self.MVN = MVN()
        self.load_loader()

    def load_loader(self):
        self.MVN.CI = 4
        with open(".\loader.hex","r") as file:
            for line in file:
                #Carrega o loader "manualmente"
                line_clean = line.strip().split()
                endr,value = int(line_clean[0],16),int(line_clean[1],16) 
                self.MVN.MEM[endr] = value

    def run(self,loader=False):
        if not loader:
            print("================\nEXECUTANDO SIMULADOR\n=================")
        #Lê os próximos dois bytes de instrução
        contador = 0
        self.MVN.state = 1
        next_i = self.MVN.readByte(self.MVN.CI)
        next_i1 = self.MVN.readByte(self.MVN.CI+1)
        #Caso sejam \00\00 o programa termina
        while (next_i != 0x00 or next_i1 != 0x00) and self.MVN.state == 1:

            self.MVN.execute_step()
            #Atualiza a proxima instrução para verificação 
            next_i = self.MVN.readByte(self.MVN.CI)
            next_i1 = self.MVN.readByte(self.MVN.CI+1)
            contador += 1
        if not loader:
            print("=================Terminou de executar===================")

    def load(self,file):
        print("================\nEXECUTANDO LOADER\n=================")
        # Carrega o aquivo a ser lido em um buffer
        self.MVN.buffer = open(file,"r").read().strip()
        print(self.MVN.buffer)
        self.run(True)
        #Pega a primeira instrução valida da posição 0x0 e 0x1
        #(Feito pelo loader) 
        b1 = self.MVN.readByte(0) << 8
        b0 = self.MVN.readByte(1)
        endr = b1 + b0
        self.MVN.CI = endr
        self.dump()
        print("=================Terminou de carregar===================")

    def dump(self,name="dump",ini=0x0,end=0xfff):
        out = open(f"{name}.txt","w+")
        dump_format = ""
        ini = ini & 0xFF0
        for endr in range(ini,end+1,16):
            endr_str = f"{endr:03x}"
            mem_str = " ".join([f"{i:02x}" for i in self.MVN.MEM[endr:endr+16]])
            dump_format += endr_str + " " + mem_str + "\n"

        out.write( dump_format)
        out.close()

#sim = Simulador()
#sim.load(".\codigo.hex")
#sim.run()
#sim.dump()