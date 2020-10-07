from mvn import Simulador
class SistemaOperacional:
    def __init__(self, mvn):
        self.mvn = mvn
        self.mvn.sistop = self

        self.overlay_table = {'root':[0,0,[]]}
        self.last_overlay = 'root'

    #=====================
    # Monitor de overlay
    #=====================

    def add_overlay(self, name):
        self.overlay_table[name] = [0,0,[]]
        self.current_overlay = name

    def set_overlay_pointers(self, ini, end, overlay=None):
        if not overlay:
            overlay = self.current_overlay

        self.overlay_table[overlay][0] = ini
        self.overlay_table[overlay][1] = end

    def monitor_de_overlay(self):
        action = self.readByte(self.CI + 3)
        overlay_n = self.readByte(self.CI + 4)
        if action == 2:
            print("set pointers")
            ENDR_INI = self.mvn.read_buffer(4)
            ENDR_END = self.mvn.read_buffer(4)
            self.set_overlay_pointers(ENDR_INI, ENDR_END)
        elif action == 1:
            #self.mvn.load()
            print("activate",overlay_n)
        elif action == 0:
            print("deactivate",overlay_n)

    def gerenciador_memoria(self):
        pass

    def gerenciador_processo(self):
        pass

mvn = Simulador()
so = SistemaOperacional(mvn)
so.mvn.run('teste_overlay1.hex')