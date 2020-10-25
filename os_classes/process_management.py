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

    def get_CI(self):
        page_num = (self.CI & 0x100) >> 8
        offset = self.pages[page_num].ram_pos - 0x100
        ci = offset + self.CI
        print(hex(offset), hex(ci))
        return ci

    def set_CI(self, mvn_CI):
        pass




    