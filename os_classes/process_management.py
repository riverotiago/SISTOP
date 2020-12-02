class ProcessControlBlock():
    def __init__(self, id, tipo):
        self.ID = id
        self.CI = 0
        self.AC = 0
        self.state = 1
        self.tipo = tipo
        self.pages = {}

    def get_page_num(self, endr):
        return (endr & 0x100) >> 8

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

        page_num = (endr & 0x100) >> 8


        offset = self.pages[page_num].ram_pos - 0x100
        ci = offset + endr
        return ci

    def set_CI(self, mvn_CI):
        # Acha qual o equivalente virtual
        page_num = (self.CI & 0x100) >> 8
        offset = self.pages[page_num].ram_pos - 0x100
        ci = mvn_CI - offset
        # Acha a página que ele corresponde
        page_num2 = (ci >> 8)
        # Se a página estiver carregada, mudar o CI
        if self.is_loaded(ci):
            self.CI = ci
            return 0
        # Se não estiver, retornar o número da página
        # para que o sistema operacional carregue
        else:
            return page_num2

    def is_loaded(self, endr):
        page_num = (endr & 0x100) >> 8
        return self.pages[page_num].isloaded





    