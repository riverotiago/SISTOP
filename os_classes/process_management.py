class ProcessControlBlock():
    def __init__(self, id, tipo):
        self.ID = id
        self.CI = 0
        self.AC = 0
        self.state = 1
        self.tipo = tipo
        self.div_table = {}
        self.pages = {}

    def get_page(self, endr):
        return self.pages[self.get_page_num(endr)]

    def get_page_num(self, endr):
        return (endr & 0xF00) >> 8

    def dispositivo(self, parametros):
        self.parametros = parametros

    def allocate(self, ram_idx, page_num):
        page = self.pages[page_num]
        page.setLoaded(ram_idx)
        return page

    def deallocate(self, storage_idx, page_num):
        page = self.pages[page_num]
        page.setStored(storage_idx)
        return page

    def get_CI(self, endr=None):
        if endr == None:
            endr = self.CI

        if not self.is_loaded(endr):
            return None

        page_num = self.get_page_num(endr)

        offset = self.pages[page_num].ram_pos 
        ci = offset + (endr & 0xFF)
        return ci

    def set_CI(self, sistop, mvn_CI):
        # Encontra a página na qual o processo se encontra
        ram_page_num = self.get_page_num(mvn_CI)
        ram_page = sistop.loaded_pages[ram_page_num]
        if ram_page:
            process_CI = (ram_page.virtual_pos << 8) + (mvn_CI & 0xFF)
            self.CI = process_CI

    def is_loaded(self, endr):
        page_num = self.get_page_num(endr)
        return self.pages[page_num].isloaded





    