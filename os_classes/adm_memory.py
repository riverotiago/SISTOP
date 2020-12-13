class AdminMemoria():

    def __init__(self, tipo, mvn, sistop):

        #===============
        # Comuns
        #===============
        self.mvn = mvn
        self.sistop = sistop
        self.ram = self.mvn.MEM
        self.hd = self.mvn.HD

        #===============
        # Páginas
        #===============
        # Página, Base,  
        self.loaded_pages = {}
        self.stored_pages = {}

        #===============
        # Segmentação
        #===============
        # Segmento, Base, Tamanho
        self.loaded_segments = {}
        self.stored_segments = {}

    def acessar(self, endr):
        pass

    def gravar(self, endr, bytes):
        pass

    def _carregar_ram(self, *args):
        pass

    def _carregar_segmentos(self, *args):
        pass

    def _carregar_paginas(self, *args):
        ini, end = args



    def _guardar_hd(self, *args):
        pass

    def _guardar_ram(self, *args):
        pass

    def _swap(self, *args):
        pass

    def _traduzir(self, N, offset):
        process = self.sistop.get_current_process()
        div = process.div_table[N]
        endr = div["base"] + offset 
        return endr if offset < div["tamanho"] else None


        
