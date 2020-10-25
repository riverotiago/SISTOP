class ProcessControlBlock():
    def __init__(self, id, tipo):
        self.ID = id
        self.CI = 0
        self.AC = 0
        self.state = 1
        self.tipo = tipo
        self.pages = {}

    def dispositivo(self, parametros):
        pass

    def allocate(self, offset, page_num):
        page = self.pages[page_num]
        page.setLoaded(offset)
        return page



    