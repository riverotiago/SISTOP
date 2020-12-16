class ProcessControlBlock():
    def __init__(self, id, tipo):
        self.ID = id
        self.CI = 0
        self.AC = 0
        self.state = 1
        self.tipo = tipo
        self.time = 0
        self.div_table = {}

    def dispositivo(self, *args):
        pass



    