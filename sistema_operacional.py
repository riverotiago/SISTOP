from mvn import Simulador
import random
from os_classes.process_management import ProcessControlBlock
from os_classes.pages import Page

##
## TODO -> Implementar: load na RAM de uma página
## sem estar previamente no storage
##

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

        # Paginas 
        self.initialize_pages()
        self.loaded_pages = {i:None for i in range(self.N_PAGES_RAM)}
        self.free_pages = set((i for i in range(1,self.N_PAGES_VIRTUAL)))

        # Processos
        self.ProcessList = {}
        self.current_process = 0

        # Dispositivos
        self.dispositivos = []


    #=====================
    # Loader
    #=====================
    def load_context_retrieve(self):
        return self.context

    def start_loader(self):
        """ Salvar estado da MVN. """
        self.context = [self.mvn.state, self.mvn.CI, self.mvn.AC]

    def end_loader(self):
        s, c, a = self.load_context_retrieve()
        self.mvn.state = s
        self.mvn.CI = c
        self.mvn.AC = a
        if not self.load:
            self.mvn.state = 0

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
    # Memória Paginada
    #=====================

    def get_current_page(self):
        pass

    def is_page_loaded(self, endr):
        return 0

    def page_store(self, storage_idx, bytes):
        """ Insere uma página na memória secundária """
        pass

    def page_load(self, ram_idx, bytes):
        """ Insere uma página na memória ram. """
        pass

    def page_swap(self, ram_idx, storage_idx):
        """ Troca uma página da ram com a memória secundária. """
        pass

    def create_page(self, RAM, HD, pagen, pagesize):
        page = Page(RAM, HD, pagen, pagesize)
        return page

    def do_page_table(self, endr):
        """ Realiza a conversão do endereço virtual para o endereço da memória física. """
        if endr < self.PAGE_SIZE:
            return endr
        else:
            return self.get_current_process().get_CI(endr)

    def initialize_pages(self):
        self.VIRTUAL_SPACE = 65536
        self.PAGE_SIZE = 256
        self.N_PAGES_VIRTUAL = int(self.VIRTUAL_SPACE/self.PAGE_SIZE)
        self.N_PAGES_RAM = int(4096/self.PAGE_SIZE)

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
        print("\n\n:: Carregando programa")
        self.mvn.load_buffer(filepath)
        print(":: Buffer >", self.mvn.buffer)

        # Recarrega os limites
        self.mvn.CI = 0x10
        for _ in range(11):
            self.mvn.state = 1
            self.mvn.run_step()

        # Limites
        ini = self.mvn.readPointer(0x5)
        end = self.mvn.readPointer(0x7)
        l = (end - ini)
        print(f':: {ini:04X} {end:04X} size:{l} bytes')

        # Calcula número de páginas
        npages = 1 + l//self.PAGE_SIZE
        print(f":: Tamanho de <{npages}> página.")

        # Cria processo
        process = self.create_process(0, None)
        print(f":: Processo <{process.ID}> criado.")

        # Cria as páginas 
        for page_num in range(1,npages+1):
            page = self.create_page(self.mvn.MEM, self.mvn.HD, page_num, self.PAGE_SIZE)
            page.processID = process.ID
            process.pages[page_num] = page
            print(f":: Criando pagina <{page_num}>")

        # Allocate page load space 
        any_offset = random.randint(1,self.N_PAGES_RAM-npages)
        for page_num in range(1,npages+1):
            offset = page_num + any_offset - 1
            self.loaded_pages[offset] = process.allocate(offset, page_num)
        
        print(f":: Resumo: {npages} páginas, alocada a partir da particao <{offset}> ")

        # Carrega na memória RAM
        print(":: Carregando programa na RAM")
        self.mvn.reg_offset = (any_offset)*self.PAGE_SIZE - ini
        print( hex((any_offset)*self.PAGE_SIZE ))
        self.mvn.state = 1
        while self.mvn.reg_loading:
            self.mvn.run_step()
        self.mvn.reg_offset = 0

        # Pointer to first instruction
        process.CI = ini

        print(":: Fim do carregamento na RAM")
        print(":: DUMP:")
        print(self.mvn.dump(ini*any_offset, ini*any_offset + l))
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

    #=====================
    # Multiprogramação
    #=====================
    def multiprog(self):
        for id in self.ProcessList.keys():
            process = self.ProcessList[id]

            if process.state == 0: continue # Pula processos finalizados

            self.current_process = process
            #print(f'>> Multiprogramacao CI={process.CI:04X}')
            # Retrieve
            self.mvn.state = process.state
            self.mvn.CI = process.get_CI()
            self.mvn.AC = process.AC
            # Execute
            self.mvn.run_step()
            # Check for end
            if self.mvn.state == 0:
                print(f"Processo <{id}> terminou. ")
            # Save
            process.state = self.mvn.state 
            toload = process.set_CI(self.mvn.CI)
            self.page_load(process, toload)
            process.AC = self.mvn.AC 

    #=====================
    # Executar código
    #=====================
    def run(self):
        while self.ProcessList:
            self.multiprog()

mvn = Simulador()
so = SistemaOperacional(mvn)

# Load program
so.load_program('print10.hex')
print(so.loaded_pages)
print(so.ProcessList)

# Run
so.run()