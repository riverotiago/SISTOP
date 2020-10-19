from mvn import Simulador
import random
from os_classes.process_management import ProcessControlBlock

class SistemaOperacional:
    def __init__(self, mvn):
        self.mvn = mvn
        self.mvn.sistop = self

        # Overlays
        self.overlay_table = {'root':[0,0,[]]}
        self.current_overlay = 'root'

        # Paginas 
        self.loaded_pages = {}
        self.initialize_pages()
        self.empty_pages_num = set(range(1,len(self.mvn.MEM) // self.PAGE_SIZE))

        # Processos
        self.ProcessList = {}
        self.current_process = 0

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
    def to_page_num(self, endr):
        ''' Calcula a página virtual em que se localiza o endereço. '''
        return f'{endr // self.PAGE_SIZE}'

    def get_page_idx(self, processID, endr):
        ''' Retorna o index para identificação de uma página virtual de um processo. '''
        return f'{processID}-{self.to_page_num(endr)}'

    def get_empty_page(self):
        ''' Retorna o número da primeira página vazia disponível na memória física. '''
        return min(self.empty_pages_num)

    def get_current_page(self):
        ''' Retorna o número da página do endereço atual na memória física. '''
        process = self.ProcessList[self.current_process]
        idx = self.get_page_idx(process.ID, self.mvn.CI)
        return idx

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

    def in_main_memory(self, processID, endr):
        ''' Retorna a página se estiver na memória física. '''
        idx = self.get_page_idx(processID, endr)
        try:
            return self.loaded_pages[idx]
        except:
            return None

    def in_storage(self, processID, endr):
        ''' Retorna a página da memória secundária (HD). '''
        idx = self.get_page_idx(processID, endr)
        return self.mvn.HD[idx]

    def do_page_table(self, endr):
        ''' Converte um endereço no espaço virtual para o espaço físico. '''
        # Se o endereço estiver na página 0 (kernel), retorna o endereço
        if endr < self.PAGE_SIZE:
            return endr

        # Checa se a página do endereço está na memória principal
        page = self.in_main_memory(self.current_process, endr)
        if page:
            # Se sim: aplica offset e retorna o novo endereço
            return endr + page['main_num']*self.PAGE_SIZE
        else:
            # Se não: busca a página na memória 
            process = self.ProcessList[self.current_process]
            storage_idx = self.get_page_idx(process.ID, endr)
            empty_page_num = self.get_empty_page()

            if not empty_page_num == None:
                # Swap com uma página vazia
                self.page_swap(storage_idx, empty_page_num)
            else:
                # Se não houver pagina vazia: swap com uma página aleatória
                idx_list = self.loaded_pages.keys()
                ridx = random.randint(0,len(idx_list))
                main_idx = idx_list[ridx]
                self.page_swap(storage_idx, main_idx)

    def initialize_pages(self):
        self.VIRTUAL_SPACE = 65536
        self.PAGE_SIZE = 256
        self.N_PAGES = self.VIRTUAL_SPACE/self.PAGE_SIZE
        self.pages = [ {'num':n,
                        'main_num':0,
                        'processid':None,
                        'protected':False,
                        } for n in range(self.N_PAGES) ]

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

    def create_process(self):
        processID = self.new_processID()
        self.ProcessList[processID] = ProcessControlBlock(processID)

    #=====================
    # Multiprogramação
    #=====================
    def multiprog(self):
        for id in self.ProcessList:
            process = self.ProcessList[id]
            # Retrieve
            self.mvn.state = process.state
            self.mvn.CI = process.CI
            self.mvn.AC = process.AC
            # Execute
            self.mvn.run_step()
            # Save
            process.state = self.mvn.state 
            process.CI = self.mvn.CI 
            process.AC = self.mvn.AC 

    #=====================
    # Executar código
    #=====================
    def run(self):
        pass

mvn = Simulador()
so = SistemaOperacional(mvn)
so.mvn.run('teste_overlay1.hex')