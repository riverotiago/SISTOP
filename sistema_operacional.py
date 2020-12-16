from mvn import Simulador
import random
from os_classes.process_management import ProcessControlBlock
from os_classes.pages import Page
from os_classes.adm_memory import AdminMemoria

class SistemaOperacional:
    def __init__(self, mvn):
        self.mvn = mvn
        self.mvn.sistop = self
        self.load = True
        self.context = []
        self.time = 0

        # Overlays
        self.overlay_table = {'root':[0,0,[]]}
        self.current_overlay = 'root'

        # Memoria
        tipo = 'segmento'
        i = input("Qual tipo de memória?\n1. paginada\n2. segmentada.\n>> ")
        if i == 1:
            tipo = 'paginada'
        self.mem_admin = AdminMemoria(tipo, self.mvn, self)

        # Processos
        self.ProcessList = {}
        self.current_process = 0
        self.garbage = []

        # Dispositivos
        self.dispositivos = []

    #=====================
    # Loader
    #=====================
    def add_constant(self):
        self.last_bytes_loaded = 1

    def add_instruction(self):
        self.last_bytes_loaded = 3

    def save_context(self):
        self.context = [self.mvn.state, self.mvn.CI, self.mvn.AC]

    def load_context(self):
        return self.context

    def loader(self, base=0, nbytes=0):
        ''' Carrega N bytes de um programa a partir do endereço base.
            Retorna 1 enquanto houver programa a ser carregado,
            Retorna 0 quando todos os bytes do programa forem carregados.
        '''
        info = self.mvn.peek_buffer(4)
        next_endr = int(info, 16)
        offset = next_endr # Garante o primeiro endereço = base
        print(f":: -> Carregando {base:04X}")
        print(f":: -> Limites {offset:04X}, {offset+nbytes:04X}")
        # Enquanto o próximo endereço não ultrapassar o limite, ou
        # até chegar ao Fim: carregar 1 byte no endereço + base
        try:
            while (not nbytes) or (next_endr < offset + nbytes):
                endr, b = self.mvn.read_buffer(4), self.mvn.read_buffer(2)
                #print(f"L {endr:04X} {b:02X}")
                self.mvn.storeByte( base + endr - offset, b)

                info = self.mvn.peek_buffer(4)
                next_endr = int(info, 16)
            return 1
        except:
            return 0

    #=====================
    # Monitor de overlay
    #=====================

    def add_overlay(self, name):
        self.overlay_table[name] = [0,0,self.current_overlay]
        self.current_overlay = name
    
    def remove_overlay(self):
        self.current_overlay = self.get_last_overlay()

    def set_overlay_pointers(self, ini, end, overlay=None):
        if not overlay:
            overlay = self.current_overlay

        self.overlay_table[overlay][0] = ini
        self.overlay_table[overlay][1] = end
    
    def get_ini_pointer(self):
        return self.overlay_table[self.current_overlay][0]

    def get_end_pointer(self):
        return self.overlay_table[self.current_overlay][1]

    def get_last_overlay(self):
        return self.overlay_table[self.current_overlay][2]

    def monitor_de_overlay(self):
        action = self.mvn.readByte(self.mvn.CI + 3)
        overlay_n = self.mvn.readByte(self.mvn.CI + 4)
        if action == 2:
            ENDR_INI = self.mvn.read_buffer(4)
            ENDR_END = self.mvn.read_buffer(4)
            self.set_overlay_pointers(ENDR_INI, ENDR_END)
            return ENDR_INI, ENDR_END
            #print("set pointers", ENDR_INI, ENDR_END,self.overlay_table)
        elif action == 1:
            print("activate overlay ",overlay_n)
            self.mvn.offset(self.get_end_pointer())
            self.add_overlay(overlay_n)
            saveCI = self.mvn.CI
            self.mvn.load(f'overlay{overlay_n}.hex', goto=saveCI-1)
            self.mvn.offset(0)

        elif action == 0:
            print("deactivate overlay ",overlay_n)
            self.remove_overlay()
            self.mvn.updateCI( self.mvn.CI - 1 )

    #=====================
    # Memória Admin
    #=====================
    def mem_acessar(self, endr):
        process = self.get_current_process()
        return self.mem_admin.acessar(process, endr)

    #=====================
    # Memória Paginada
    #=====================
    def initialize_pages(self):
        self.VIRTUAL_SPACE = 65536
        self.PAGE_SIZE = 256
        self.N_PAGES_VIRTUAL = int(self.VIRTUAL_SPACE/self.PAGE_SIZE)
        self.N_PAGES_RAM = int(len(self.mvn.MEM)/self.PAGE_SIZE)
        self.N_PAGES_STORAGE = int(len(self.mvn.HD)/self.PAGE_SIZE)

    #=====================
    # Administrador de Processos
    #=====================
    def get_current_process(self):
        return self.current_process

    def new_processID(self):
        ''' Retorna o menor id de processo disponível. '''
        ids = self.ProcessList.keys()
        if not ids:
            return 0

        N = max(ids)
        for k in range(N+1):
            if not k in ids:
                return k
        return N+1

    def create_process(self, tipo, payload):
        # Cria process control block
        processID = self.new_processID()
        process = ProcessControlBlock(processID, tipo)
        self.ProcessList[processID] = process

        if tipo == 0: # Código
            pass

        elif tipo == 1: # Dispositivo
            parameters = payload
            process.dispositivo(parameters)

        return process

    def destroy_process(self):
        # Garbage collect
       pass 

    def load_program(self, filepath):
        print("\n\n:: Carregando programa", filepath)
        if '.hex' in filepath:
            self.mvn.load_buffer(filepath)
        elif '.seg' in filepath:
            self.mem_admin.seg_list(filepath)

        #print(":: Buffer >", self.mvn.buffer)

        # Cria processo
        process = self.create_process(0, None)
        process.filepath = filepath
        print(f":: Processo <{process.ID}> criado.")

        # Pega os limites do endereço 
        ini, end = self.mem_admin.get_limites()
        print(f":: Limites {ini}, {end}")

        # Carrega o programa na memória
        self.mem_admin.process_memory(process)

        # Pointer to first instruction
        process.CI = ini

        print("::\n\n")

    #=====================
    # Administração dispositivos
    #=====================

    def registrar_dispositivo(self, process, tipo):
        parametros = None
        if tipo == 0: # Mouse
            parametros = {'tempo_processmento':3}
        elif tipo == 1: # Impressora 
            parametros = {'tempo_processmento':10, 'ocupado':False}
        elif tipo == 2: # Teclado
            parametros = {'tempo_processmento':5}

        # Coloca o dispositivo na lista de dispositivos
        self.dispositivos.append( process.dispositivo(parametros) )

    def elapsed_time(self, dispositivo):
        return self.time - dispositivo.last()

    def IO(self):
        print("E/S", end=', ')

    #=====================
    # Multiprogramação
    #=====================
    def multiprog(self):
        for id in self.ProcessList.keys():
            process = self.ProcessList[id]

            if process.state == 0: continue # Pula processos finalizados
            print(f"Processo {id} ({process.time}ms): ",end='')

            # Recupera dados do processo
            self.current_process = process
            self.mvn.state = process.state

            # Recupera o CI atual do processo,
            self.mvn.CI = self.mem_admin.acessar(process, process.CI)
                
            # Mantem a divisão em execução fixa
            #idx = self.mem_admin.keep(self.mvn.CI)

            # Execute
            self.mvn.AC = process.AC
            self.mvn.run_step()
            process.time += self.mvn.delta 

            # Libera a divisão de estar fixa
            #self.mem_admin.unkeep(idx)

            print('')
            # Check for end
            if self.mvn.state == 0:
                self.garbage.append(id)
                print(f"Processo <{id}> terminou com {process.time}ms de execução. ")
            else:
                # Save
                process.state = self.mvn.state 
                process.CI = self.mem_admin._desconverter(self.mvn.CI)
                process.AC = self.mvn.AC 

    #=====================
    # Executar código
    #=====================
    def run(self):
        running = True
        processes = []
        while running:
            self.multiprog()
            #print(f"==========\nMVN Elapsed {self.mvn.time}ns")

            # Remove processos não utilizados
            if self.garbage:
                while len(self.garbage) > 0:
                    id = self.garbage.pop()
                    print(f":: Garbage collector -> Processo {id}")
                    processes.append(self.ProcessList[id])
                    del self.ProcessList[id]

            running = self.ProcessList
        
        print(" Resumo de execução: ")
        for p in processes:
            print(f"Processo <{p.ID}> rodou por {p.time}ms; ")
        print(" Mapa da memória final: ") 
        print(self.mem_admin.segment_map)
        print("")
        

mvn = Simulador()
so = SistemaOperacional(mvn)

# Load program
#so.load_program('print10_v2.seg')
so.load_program('p1.seg')
so.load_program('p2.seg')
so.load_program('p3.seg')
so.load_program('p4.seg')
print("Páginas carregadas\n")
print("Processos\n",so.ProcessList,"\n")

# Run
so.run()