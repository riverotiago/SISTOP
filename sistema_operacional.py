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
    def load_context_save(self):
        self.context = [self.mvn.state, self.mvn.CI, self.mvn.AC]
    
    def load_context_retrieve(self):
        return self.context

    def load_admin(self):
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
    """
    def page_swap(self, storage_idx, main_idx):
        ''' Troca uma página do HD (page_idx) com uma página da memória física (to_swap). '''
        # Swap com uma pagína vazia da memória física
        if main_idx in self.empty_pages_num:
            # Remove o indice vazio
            self.empty_pages_num.remove(main_idx)
            # Recupera a pagina do storage
            page = self.mvn.HD[storage_idx]
            # Substitui o número da página na memória física
            page['main_num'] = main_idx
            self.loaded_pages[storage_idx] = page
            # Remove a página do storage
            del self.mvn.HD[storage_idx]
        # Swap com uma página ocupada da memória física
        else:
            page_main = self.loaded_pages[main_idx]
            page_storage = self.mvn.HD[storage_idx]
            # Update
            page_storage['main_num'] = page_main['main_num']
            page_main['main_num'] = 0
            # Troca
            self.loaded_pages[storage_idx] = page_storage
            self.mvn.HD[main_idx] = page_main
        """
    #===================================
    def page_store(self, storage_idx, bytes):
        """ Insere uma página na memória secundária """
        pass


    def page_load(self, ram_idx, bytes):
        """ Insere uma página na memória ram. """
        pass


    def page_swap(self, ram_idx, storage_idx):
        """ Troca uma página da ram com a memória secundária. """
        pass

    def do_page_table2(self, endr):
        if endr < self.PAGE_SIZE:
            return endr

        # Checa se o endereço está em um página carregada
        page_idx = self.is_page_loaded(endr)

        if page_idx:
            pass
        else:
            self.page_swap( self.get_ci(), page_idx)


    #===================================
    """

    def getProcess(self, processID):
        return self.ProcessList[processID]

    def in_main_memory(self, processID, endr):
        ''' Retorna a página se estiver na memória física. '''
        process = self.getProcess(self.current_process)

    def in_storage(self, processID, endr):
        ''' Retorna a página da memória secundária (HD). '''
        idx = self.get_page_idx(processID, endr)
        return self.mvn.HD[idx]

    def do_page_table(self, endr):
        ''' Converte um endereço no espaço virtual para o espaço físico. '''
        # Se o endereço estiver na página 0 (kernel), retorna o endereço
        #print('    -do page table')
        if endr < self.PAGE_SIZE:
            print(f'        -return {endr}')
            return endr

        # Checa se a página do endereço está na memória principal
        page = self.in_main_memory(self.current_process, endr)
        if page:
            # Se sim: aplica offset e retorna o novo endereço
            return endr + page['main_offset']*self.PAGE_SIZE
        else:
            # Se não: busca a página na memória 
            process = self.ProcessList[self.current_process]
            storage_idx = self.get_page_idx(process.ID, endr)
            #empty_page_num = self.get_empty_page()

            if not process == None: # empty virou process
                # Swap com uma página vazia
                #self.page_swap(storage_idx, empty_page_num)
                page = self.loaded_pages[storage_idx]
                return endr + page['main_offset']*self.PAGE_SIZE
            else:
                # Se não houver pagina vazia: swap com uma página aleatória
                idx_list = self.loaded_pages.keys()
                ridx = random.randint(0,len(idx_list))
                main_idx = idx_list[ridx]
                #self.page_swap(storage_idx, main_idx)
                page = self.loaded_pages[storage_idx]
                return endr + page['main_offset']*self.PAGE_SIZE

    def create_page(self, RAM, HD, pagen, pagesize):
        page = Page(RAM, HD, pagen, pagesize)
        return page

    def allocate_space(self, npages):
        for page_num in range(1,npages+1):
            offset = page_num + any_offset
            self.loaded_pages[offset] = process.allocate(offset, page_num)

    def swap(self, ram_offset=None, hd_offset=None):
        ram_pos = ram_offset * self.PAGE_SIZE
        hd_pos = hd_offset * self.PAGE_SIZE
        ram = slice(ram_pos, ram_pos+self.PAGE_SIZE)
        hd = slice(hd_pos, hd_pos+self.PAGE_SIZE)
        self.mvn.MEM[ram], self.mvn.HD[hd] = self.mvn.HD[hd], self.mvn.MEM[ram]
    
    def load_page(self, process, page_num):
        # Recupera o índice de armazenamento da pagina
        page = process.pages[page_num]
        hd_offset = page.hd_pos >> 8

        # Se página não está no hd
        if not page.isstored:
            any_hd_offset = random.randint(1,self.N_PAGES_VIRTUAL-len(process.pages))


        # Seleciona uma página aleatória para substituir
        any_offset = random.randint(1,self.N_PAGES_RAM-len(process.pages))
        # Se a página aleatória está carregada, swap, se não, load
        if self.loaded_pages[any_offset]:
            self.swap(any_offset, hd_offset)

            self.loaded_pages[any_offset] = process.allocate(any_offset, page_num)

            alreadyloaded = self.loaded_pages[any_offset]
            process.deallocate(hd_offset, alreadyloaded.virtual_pos)
            
        else:
            self.loaded_pages[any_offset] = process.allocate(any_offset, page_num)

    """

    def initialize_pages(self):
        self.VIRTUAL_SPACE = 65536
        self.PAGE_SIZE = 256
        self.N_PAGES_VIRTUAL = int(self.VIRTUAL_SPACE/self.PAGE_SIZE)
        self.N_PAGES_RAM = int(4096/self.PAGE_SIZE)

    #=====================
    # Administrador de Processos
    #=====================

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
        print("Loading")
        self.mvn.load_buffer(filepath)

        # Recarrega os limites
        self.mvn.CI = 0x10
        for _ in range(11):
            self.mvn.state = 1
            self.mvn.run_step()

        # Limites
        print(self.mvn.MEM[:10])
        ini = self.mvn.readPointer(0x5)
        end = self.mvn.readPointer(0x7)
        l = (end - ini)
        print(f'{ini:04X} {end:04X} size:{l} bytes')

        # Calcula número de páginas
        npages = 1 + l//self.PAGE_SIZE

        # Cria processo
        process = self.create_process(0, None)

        # Cria as páginas 
        for page_num in range(1,npages+1):
            page = self.create_page(self.mvn.MEM, self.mvn.HD, page_num, self.PAGE_SIZE)
            page.processID = process.ID
            process.pages[page_num] = page

        # Allocate page load space 
        any_offset = random.randint(1,self.N_PAGES_RAM-npages)
        for page_num in range(1,npages+1):
            offset = page_num + any_offset
            self.loaded_pages[offset] = process.allocate(offset, page_num)
        
        print(f"Resumo: {npages} páginas, {offset} offset")

        # Carrega na memória RAM
        print("loading RAM")
        self.mvn.reg_offset = any_offset*self.PAGE_SIZE
        self.mvn.state = 1
        while self.mvn.reg_loading:
            self.mvn.run_step()
        self.mvn.reg_offset = 0

        # Pointer to first instruction
        process.CI = ini

        print("finished loading RAM")

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
            print('multiprog',process.CI)
            # Retrieve
            self.mvn.state = process.state
            self.mvn.CI = process.get_CI()
            self.mvn.AC = process.AC
            # Execute
            self.mvn.run_step()
            # Check for end
            if self.mvn.state == 0:
                del self.ProcessList[id]
            # Save
            process.state = self.mvn.state 
            toload = process.set_CI(self.mvn.CI)
            self.load_page(process, toload)
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
so.load_program('print100.hex')
print(so.loaded_pages)
for v in so.loaded_pages.values():
    if v:
        pointer = v.getPointer()
        print(so.mvn.dump(pointer, pointer+0x20))

print(so.ProcessList)

# Run
so.run()