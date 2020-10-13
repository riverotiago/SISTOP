from mvn import Simulador
from os_classes.process_management import ProcessTable

class SistemaOperacional:
    def __init__(self, mvn):
        self.mvn = mvn
        self.mvn.sistop = self

        # Overlays
        self.overlay_table = {'root':[0,0,[]]}
        self.current_overlay = 'root'

        # Paginas 
        self.initialize_pages()

        # Processos

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
    def page_swap(self):
        pass

    def initialize_pages(self):
        n_pages = 8
        page_size = 65536
        self.pages = [ {} for i in range(n_pages) ]

    #=====================
    # Administrador de Processos
    #=====================
    def new_processID(self):
        return 0

    def create_process(self):
        pass

    #=====================
    # Executar código
    #=====================

    def run(self):
        pass

mvn = Simulador()
so = SistemaOperacional(mvn)
so.mvn.run('teste_overlay1.hex')