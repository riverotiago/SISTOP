from mvn import Simulador
class SistemaOperacional:
    def __init__(self, mvn):
        self.mvn = mvn
        self.mvn.sistop = self
        self.overlay_table = {'root':[0,0]}

    def monitor_de_overlay(self):
        action = self.readByte(self.CI + 3)
        overlay_n = self.readByte(self.CI + 4)
        if action == 2:
            print("set root pointers")
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