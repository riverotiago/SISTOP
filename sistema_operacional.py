from mvn import Simulador
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
        self.empty_pages_num = set(range(len(self.mvn.MEM) // self.PAGE_SIZE))

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
    def get_empty_page(self):
        ''' Retorna o número da primeira página vazia disponível na memória física. '''
        return min(self.empty_pages_num)

    def get_current_page(self):
        ''' Retorna o número da página do endereço atual na memória física. '''
        process = self.ProcessList[self.current_process]
        idx = f'{process.ID}-{self.to_page_num(process.CI)}'
        num = self.loaded_pages[idx]['main_page']
        return num

    def page_swap(self, page, to_swap_page_num):
        page['main_page'] = to_swap_page_num
        self.loaded_pages[to_swap_page_num] = page
        # Falta fazer loader

    def to_page_num(self, endr):
        ''' Calcula a página virtual em que se localiza o endereço. '''
        return f'{endr // self.PAGE_SIZE}'

    def in_main_memory(self, processID, endr):
        ''' Retorna a página se estiver na memória. '''
        idx = f'{processID}-{self.to_page_num(endr)}'
        try:
            return self.loaded_pages[idx]
        except:
            return None

    def in_storage(self, page):
        ''' Retorna a página da memória secundária (HD). '''
        ini = page*self.PAGE_SIZE
        end = ini+self.PAGE_SIZE
        return self.mvn.HD[ini:end]

    def do_page_table(self, endr):
        ''' Converte um endereço no espaço virtual para o espaço físico. '''
        # Checa se a página do endereço está na memória principal
        page = self.in_main_memory(self.current_process, endr)
        if page:
            # Se sim: aplica offset e retorna o novo endereço
            return endr + page['offset']
        else:
            # Se não: busca a página na memória 
            page_storage_num = self.ProcessList[self.current_process].get_page_storage(endr)
            page = self.in_storage(page_storage_num)
            empty_page_num = self.get_empty_page()

            if not empty_page_num == None:
                # Swap com uma página vazia
                self.page_swap(page, empty_page_num)
            else:
                # Se não houver pagina vazia: swap com a página seguinte
                self.page_swap(page, self.get_current_page() + 1)

    def initialize_pages(self):
        self.VIRTUAL_SPACE = 65536
        self.PAGE_SIZE = 256
        self.N_PAGES = self.VIRTUAL_SPACE/self.PAGE_SIZE
        self.pages = [ {'offset':self.PAGE_SIZE*n,
                        'mem':bytearray(self.PAGE_SIZE),
                        'processid':None,
                        'protected':False,
                        'main_page':None } for n in range(self.N_PAGES) ]

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