from mvn import Simulador
class SistemaOperacional:
    def __init__(self, mvn):
        self.mvn = mvn
        self.mvn.sistop = self

    def monitor_de_overlay(self, action, overlay_n):
        if action == 1:
            self.mvn.load()
        elif action == 0:
            pass

    def gerenciador_memoria(self):
        pass

    def gerenciador_processo(self):
        pass

mvn = Simulador()
so = SistemaOperacional(mvn)
so.mvn.run('teste_overlay1.hex')