import random
import math

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
        self.excluded = {}
        self.keep = set()

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


    #=============
    # Public
    #=============
    def acessar(self, process, endr):
        if endr < 0x100:
            return endr

        if self.tipo == 'pagina':
            
            # Pega table
            table = process.div_table
            # Pega a página (divisão)
            div = self._get_divisao(table, endr)

            # Se a página não estiver carregada na memória, acha-la no storage 
            # e guarda-la em ram
            if not self._esta_carregada(table, endr):
                ram_idx = self.randint_exclude(1, self.N_PAGES_RAM-1, self.excluded)
                storage_idx = div['base'] // self.PAGE_SIZE

                # Se a posição de inserção já estiver ocupada
                if self.loaded.get(ram_idx, None):
                    self._guardar_swap(ram_idx, storage_idx)
                else:
                    self._guardar_ram(ram_idx, storage_idx)
            
            # Retorna o novo endereço
            endr_fisico = self._converter(table, endr)
            print(f" |-> Convertendo {endr:04X} -> {endr_fisico:04X}")
            return endr_fisico

    def process_memory(self, process):
        ''' Cria processo na memória segundo o método de administração escolhido. '''
        if self.tipo == 'pagina':
            self.process_pages(process)
        elif self.tipo == 'segmento':
            self.process_segments(process)

    #===================
    # Private
    #===================
    def _get_free_storage_idx(self):
        """ Escolhe uma posição livre do HD. """
        if not self.stored:
            return 0

        a = min(self.stored)
        b = max(self.stored)

        if a == 0 and b == self.N_PAGES_STORAGE:
            return None

        for storage_idx in range(a-1,b+2):
            if storage_idx >= 0 and storage_idx < self.N_PAGES_STORAGE and (not self.stored[storage_idx]):
                return storage_idx

    def _ativar_loader(self, base, nbytes):
        return self.sistop.loader(base, nbytes)

    def _get_divisao(self, table, endr):
        ''' Retorna a divisão em que se encontra o endereço. '''
        if self.tipo == 'pagina':
            return table[(endr & 0xF00) >> 8]

    def _converter(self, table, endr):
        ''' Converte endereço virtual em físico. '''
        div = self._get_divisao(table, endr)
        endr = div["base"] + (endr % div["tamanho"])
        return endr 

    def _desconverter(self, endr):
        ''' Converte endereço físico em virtual. '''
        if self.tipo == 'pagina':
            div = self._get_divisao(self.loaded, endr)
            return div['N']*self.PAGE_SIZE + (endr - div['base'])

    #=====================
    # Paginas
    #=====================
    def process_pages(self, process):
        # Cria as paginas e da load nelas
        self._carregar_paginas(process)

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

    def _carregar_paginas(self, process):
        N = 0
        run = 1

        while run:
            # Indice de inserção aleatório
            ram_idx = self.randint_exclude(1, self.N_PAGES_RAM-1, self.excluded)
            base = ram_idx * self.PAGE_SIZE

            print(f":: Sorteando índice <{ram_idx}>")
            # Se já houver página nesse indice
            if self.loaded.get(ram_idx, None):
                # Guarda a pagina no hd
                storage_idx = self._get_free_storage_idx()
                self._guardar_hd(self.loaded[ram_idx], storage_idx)
                print(f":: - Já há página nesse índice, guardando ela em <{storage_idx}>")

            # Cria página
            N = (int(self.mvn.peek_buffer(4), 16) & 0xF00 ) >> 8
            page = self._criar_pagina(N, base)
            process.div_table[N] = page
            self.loaded[ram_idx] = page

            print(f":: Inserindo página <{N}> na posição <{base:04X}> da ram.")

            # Escreve na ram
            run = self._ativar_loader(base, self.PAGE_SIZE)

            print(":: DUMP\n", self.mvn.dump(base, base+self.PAGE_SIZE))

    #=====================
    # Segmentos
    #=====================

    def process_segments(self, process):
        # Cria as paginas e da load nelas
        self._carregar_segmentos(process)
    
    def _carregar_segmentos(self, process):
        pass

    #=====================
    # Comuns
    #=====================

    def _guardar_hd(self, ram_idx, storage_idx):
        div = self.loaded[ram_idx]
        div['carregada'] = False
        div['base'] = storage_idx*self.PAGE_SIZE
        self.loaded[ram_idx] = None
        self.stored[storage_idx] = div
        self.byte_swap(ram_idx, storage_idx)

    def _guardar_ram(self, ram_idx, storage_idx):
        div = self.stored[storage_idx]
        div['carregada'] = True
        div['base'] = ram_idx*self.PAGE_SIZE
        self.loaded[ram_idx] = div 
        self.stored[storage_idx] = None
        self.byte_swap(ram_idx, storage_idx)

    def _guardar_swap(self, ram_idx, storage_idx):
        div_ram = self.loaded[ram_idx]
        div_storage = self.stored[storage_idx]
        div_ram['carregada'] = False
        div_storage['carregada'] = True
        div_ram['base'], div_storage['base'] = div_storage['base'], div_ram['base']
        self.loaded[ram_idx] = div_storage
        self.stored[storage_idx] = div_ram
        self.byte_swap(ram_idx, storage_idx)
        
    def byte_swap(self, ram_idx, storage_idx):
        """ Troca uma página da ram com a memória secundária. """
        ram_ptr = self.page_pointers(ram_idx)
        ram_bytes = self.ram[ram_ptr]

        hd_ptr = self.page_pointers(storage_idx)
        hd_bytes = self.hd[hd_ptr]

        # SWAP bytes
        self.ram[ram_ptr] = hd_bytes
        self.hd[hd_ptr] = ram_bytes

    def randint_exclude(self, a, b, exclude):
        r = random.randint(a,b)
        while r in exclude:
            r = random.randint(a,b)
        return r

    def page_pointers(self, idx):
        return slice(idx*self.PAGE_SIZE, (idx+1)*self.PAGE_SIZE)

        
