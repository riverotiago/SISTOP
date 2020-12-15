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
        print(f"-> Acessando endr: {endr:04X}")
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
        
        elif self.tipo == 'segmento':

            # Acha o segmento do endereço acessado
            table = process.div_table
            storage_idx, segment = self._procurar_endr(table, endr)

            # Se não estiver carregado, carrega-lo na memória
            if not self._esta_carregado(segment):
                # Acha a melhor posição para inserção
                pos = self._procurar_posicao(segment['tamanho'])
                self._alocar_segmento(storage_idx, segment, pos)
            
            # Retorna o novo endereço
            endr_fisico = (endr - segment['endr_ini']) + segment['base']
            print(f" |-> Convertendo {endr:04X} -> {endr_fisico:04X}")
            return endr_fisico

    def process_memory(self, process):
        ''' Cria processo na memória segundo o método de administração escolhido. '''
        if self.tipo == 'pagina':
            self.process_pages(process)
        elif self.tipo == 'segmento':
            self.process_segments(process)

    def get_limites(self):
        if self.tipo == "pagina":
            ini = int(self.mvn.buffer[:4],16)
            end = int(self.mvn.buffer[-6:-2],16)
        elif self.tipo == "segmento":
            ini, end = self.seg_limits

        return ini, end

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

    def _get_free_idx(self, lista):
        """ Escolhe um índice aleatório não utilizado. """
        if not lista:
            return 1

        a = min(lista)
        b = max(lista)
        
        for idx in range(1, b+2):
            if not idx in lista:
                return idx

    def _ativar_loader(self, base, nbytes=0):
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

        elif self.tipo == "segmento":
            ram_idx, segment = self._procurar_endr(self.loaded, endr)
            return endr - segment['base'] + segment['endr_ini']

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

    def seg_list(self, filepath):
        seg_list = open(filepath).read().strip().split(' ')
        self.seg_limits, self.seg_numbers = list(map(int,seg_list[:2])), \
            list(map(int, seg_list[2:]))

    def process_segments(self, process):
        # Cria os segmentos e da load neles
        self._carregar_segmentos(process)
    
    def _carregar_segmentos(self, process):
        path = process.filepath
        
        for N in self.seg_numbers:
            print(f":: Carregando o segmento {N}")
            self.mvn.load_buffer(f'{path}{N}.hex')

            # Calula tamanho do segmento
            ini = int(self.mvn.buffer[:4],16)
            end = int(self.mvn.buffer[-6:-2],16)
            tamanho = end - ini + 1

            # Cria o segmento
            base = self._procurar_posicao(tamanho)
            idx = self._get_free_idx(self.loaded) 
            self.loaded[idx] = self._criar_segmento(N, base, tamanho, ini, process)
            print(f":: - Criando segmento {N}, na base {base:04X} com tamanho {tamanho}")

            # Guarda o ponteiro para o segmento dentro do PCB
            process.div_table[N] = self.loaded[idx]

            self._ativar_loader(base)
            print(f"::DUMP\n", self.mvn.dump(base, base+tamanho))

        self._mapear_segmentos()
        print(f":: Visão da memória:", self.segment_map)

    def _criar_segmento(self, N, base, tamanho, endr_ini, process):
        return {
            'N':N,
            'base':base,
            'endr_ini':endr_ini,
            'process':process,
            'carregado': True,
            'tamanho':tamanho
        }

    def _mapear_segmentos(self):
        ''' Mapeia os espaços vazios e os espaços ocupados pelos segmentos. '''
        m = []
        B = 0x100 
        L = 0x1000
        for n in self.loaded:
            sb = self.loaded[n]['base']
            sl = self.loaded[n]['tamanho']
            if not B == sb:
                m.append( (0, B, sb - B) )
            B = sb+sl
            m.append((n, sb, sl))
        
        if not B == L:
            m.append( (0, B, L - B) )

        self.segment_map = m

    def _procurar_posicao(self, tamanho):
        ''' Procura a melhor posição para inserção do segmento. '''
        self._mapear_segmentos()
        # Loop pelos segmentos já alocados
        # Há espaço vazio?
        vazio = 0
        for s in self.segment_map:
            if s[0] == 0:
                vazio += s[2] + 1
            if s[0] == 0 >= tamanho:
                return s[1]

        # Houver, mas não contíguo, desfragmentar a ram e retornar a posição
        if vazio >= tamanho:
            return self._defrag()
        
        # Se não houver, desalocar os N menores segmentos e desfragmenta a RAM
        else:
            self._liberar_tamanho(tamanho)
            return self._defrag()

    def _defrag(self):
        ''' Realoca todos os segmentos continuamente e retorna 
            a posição de onde começa o espaço vazio.
        '''
        # Junta o final de um segmento com o final do outro 
        # a partir do inicio da memória livre (0x100)
        nova_base = 0x100
        segments = [self.loaded[n] for n in self.loaded]
        mems = [self._get_mem(segment) for segment in segments]

        for k,segment in enumerate(segments):
            # Muda a tabela
            base_temp = segment['base']
            segment['base'] = nova_base
            print(f"> Desfragmentando: base_temp: {base_temp} nova_base:{nova_base} next:{base_temp + segment['tamanho']}")
            nova_base = nova_base + segment['tamanho']
            # Muda a memória de lugar
            self.ram[base_temp:nova_base] = mems[k]

        # Atualiza o mapa de segmentos
        self._mapear_segmentos()
        return nova_base

    def _liberar_tamanho(self, tamanho):
        ''' Desaloca os N menores segmentos para liberar tamanho. '''
        # Segmentos por tamanho
        vazio = self._get_vazio()
        liberado = 0
        n = 0

        ordered_n = [i for i in sorted( self.loaded, key=lambda n: self.loaded[n]['tamanho'])]
        print(f">> ordenação", vazio, ordered_n)

        while vazio + liberado < tamanho:
            idx = ordered_n[n]
            liberado += self.loaded[idx]['tamanho'] 
            n += 1

        for k in range(n):
            idx = ordered_n[k]
            self._desalocar_segmento(idx, self.loaded[idx])

        # Atualiza o mapa de segmentos
        self._mapear_segmentos()

    def _get_vazio(self):
        ''' Retorna a quantidade de espaço vago.'''
        self._mapear_segmentos()
        return sum(s[2] for s in self.segment_map if s[0] == 0)

    def _get_mem(self, segment):
        ''' Retorna a memória compreendida pelo segmento. '''
        ini = segment['base']
        end = segment['base'] + segment['tamanho']
        if segment['carregado']:
            return self.ram[ini:end]
        else:
            return self.hd[ini:end]

    def _procurar_endr(self, tabela, endr):
        ''' Retorna o idx e o segmento que contem o endereço. '''
        for idx in tabela:
            segment = tabela[idx]
            ini = segment['endr_ini']
            end = ini + segment['tamanho']
            if segment['endr_ini'] <= endr < end:
                return idx, segment

    def _procurar_segmento(self, tabela, segment):
        ''' Retorna o idx do segmento. '''
        for idx in tabela:
            if tabela[idx] == segment:
                return segment
        return None

    def _desalocar_segmento(self, ram_idx, segment):
        ''' Faz a desalocação de um segmento na memória. '''
        print(f":: Desalocando segmento <{ram_idx}> (Processo {segment['process'].ID}, N {segment['N']})")
        segment['carregado'] = False
        mem = self._get_mem(segment)
        segment['mem'] = mem
        storage_idx = self._get_free_idx(self.stored)
        self.stored[storage_idx] = segment
        del self.loaded[ram_idx]

    def _alocar_segmento(self, storage_idx, segment, base=None):
        ''' Faz a alocação de um segmento na memória, a partir da posição base. '''
        segment['carregado'] = True
        ram_idx = self._get_free_idx(self.loaded)
        self.ram[base:base + segment['tamanho']] = segment['mem']
        self.loaded[ram_idx] = segment
        del self.stored[storage_idx]

    def _esta_carregado(self, segment):
        return segment['carregado']

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

"""
p = [(1, 1000, 2000)]
self.loaded = { k+1:self._criar_segmento(k+1, i[0], i[1]-i[0]+1) for k,i in enumerate(p)}
self._mapear_segmentos()
print(self.segment_map)
print(self._defrag())
print(self.segment_map)
print('\n',self.loaded,'\n')
print("posição encontrada",self._procurar_posicao(2000))
print('\n',self.loaded,'\n')
self._defrag()
print(self.segment_map)
"""
