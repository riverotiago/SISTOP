class ProcessControlBlock():
    def __init__(self, id, tipo):
        self.ID = id
        self.CI = 0
        self.AC = 0
        self.state = 1
        self.tipo = tipo
        self.div_table = {}
        self.pages = {}

    def dispositivo(self, *args):
        pass



    