import random

class AdminMemoria():

    def __init__(self, tipo, mvn, sistop):

        #===============
        # Comuns
        #===============
        self.tipo = tipo
        self.mvn = mvn
        self.sistop = sistop
        self.ram = self.mvn.MEM
        self.hd = self.mvn.HD
        self.RAM_SIZE = len(self.ram)
        self.STORAGE_SIZE = len(self.hd)

        self.loaded = {}
        self.stored = {}

        #===============
        # Páginas
        #===============
        # Página, Base,  
        self.VIRTUAL_SPACE = 65536
        self.PAGE_SIZE = 256
        self.N_PAGES_VIRTUAL = int(self.VIRTUAL_SPACE/self.PAGE_SIZE)
        self.N_PAGES_RAM = int(self.RAM_SIZE/self.PAGE_SIZE)
        self.N_PAGES_STORAGE = int(self.STORAGE_SIZE/self.PAGE_SIZE)

        #===============
        # Segmentação
        #===============
        # Segmento, Base, Tamanho

    def acessar(self, process, endr):
        if tipo == 'pagina':
            # Pega table
            table = process.div_table
            # Pega a página (divisão)
            div = self._get_divisao(table, endr)
            # Checa se a pagina está carregado na memória
            if self._esta_carregada(div):
                return self._converter(table, endr)
            else:
                # Se não estiver, acha-la no storage e guarda-la em ram
                self._guardar_ram(div)
                return self._converter(table, endr)

    def gravar(self, endr, bytes):
        pass

    def _ativar_loader(self, base, nbytes):
        self.sistop.loader(base, nbytes)

    def _get_divisao(self, table, endr):
        ''' Retorna a divisão em que se encontra o endereço. '''
        if tipo == 'pagina':
            return table[(endr & 0xF00) >> 8]

    def _converter(self, table, endr):
        ''' Converte endereço virtual em físico. '''
        div = self._get_divisao(table, endr)
        endr = div["base"] + (endr % div["tamanho"])
        return endr 

    def _desconverter(self, endr):
        ''' Converte endereço físico em virtual. '''
        if tipo == 'pagina':
            div = self._get_divisao(self.loaded, endr)
            return div['N']*self.PAGE_SIZE + div['base'] - endr

    #=====================
    # Paginas
    #=====================
    def _criar_pagina(self, N, base):
        return {
            "N": N,
            "base":base,
            "carregada":True,
            "tamanho":self.PAGE_SIZE
        }

    def _esta_carregada(self, table, endr):
        N = (endr & 0xF00) >> 8
        return table[N]['carregada']

    def _carregar_paginas(self, *args):
        base = randint()
        while self._ativar_loader(base, self.PAGE_SIZE):

    #=====================
    # Segmentos
    #=====================

    def _carregar_segmentos(self, *args):
        pass


    def _guardar_hd(self, *args):
        pass

    def _guardar_ram(self, *args):
        pass

    def _swap(self, *args):
        pass

    def randint_exclude(self, a, b, exclude):
        r = random.randint(a,b)
        while r in exclude:
            r = random.randint(a,b)
        return r



        
