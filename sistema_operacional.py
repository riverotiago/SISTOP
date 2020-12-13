from mvn import Simulador
import random
from os_classes.process_management import ProcessControlBlock
from os_classes.pages import Page
from os_classes.adm_memory import AdminMemoria

class SistemaOperacional:
    def __init__(self, mvn):
        self.mvn = mvn
        self.mvn.sistop = self
        self.load = True
        self.context = []
        self.time = 0

        # Overlays
        self.overlay_table = {'root':[0,0,[]]}
        self.current_overlay = 'root'

        # Memoria
        self.mem_admin = AdminMemoria('pagina', self.mvn, self)

        # Processos
        self.ProcessList = {}
        self.current_process = 0
        self.garbage = []

        # Dispositivos
        self.dispositivos = []

    #=====================
    # Loader
    #=====================
    def add_constant(self):
        self.last_bytes_loaded = 1

    def add_instruction(self):
        self.last_bytes_loaded = 3

    def save_context(self):
        self.context = [self.mvn.state, self.mvn.CI, self.mvn.AC]

    def load_context(self):
        return self.context

    def loader(self, base=0, nbytes=0):
        ''' Carrega N bytes de um programa a partir do endereço base.
            Retorna 1 enquanto houver programa a ser carregado,
            Retorna 0 quando todos os bytes do programa forem carregados.
        '''
        buffer_left = self.mvn.extrai_tamanho()
        info = self.mvn.peek_buffer(4)
        next_endr = int(info, 16)
        offset = next_endr # Garante o primeiro endereço = base
        try:
            # Enquanto o próximo endereço não ultrapassar o limite, ou
            # até chegar ao Fim: carregar 1 byte no endereço + base
            while (not nbytes) or (next_endr <= nbytes):
                endr, b = self.mvn.read_buffer(4), self.mvn.read_buffer(2)
                self.mvn.storyByte( base + endr - offset, b)

                info = self.mvn.peek_buffer(4)
                next_endr = base + int(info, 16) - offset
            return 1
        except:
            return 0

    #=====================
    # Monitor de overlay
    #=====================

    def add_overlay(self, name):
        self.overlay_table[name] = [0,0,self.current_overlay]
        self.current_overlay = name
    
    def remove_overlay(self):
        self.current_overlay = self.get_last_overlay()

    def set_overlay_pointers(self, ini, end, overlay=None):
        if not overlay:
            overlay = self.current_overlay

        self.overlay_table[overlay][0] = ini
        self.overlay_table[overlay][1] = end
    
    def get_ini_pointer(self):
        return self.overlay_table[self.current_overlay][0]

    def get_end_pointer(self):
        return self.overlay_table[self.current_overlay][1]

    def get_last_overlay(self):
        return self.overlay_table[self.current_overlay][2]

    def monitor_de_overlay(self):
        action = self.mvn.readByte(self.mvn.CI + 3)
        overlay_n = self.mvn.readByte(self.mvn.CI + 4)
        if action == 2:
            ENDR_INI = self.mvn.read_buffer(4)
            ENDR_END = self.mvn.read_buffer(4)
            self.set_overlay_pointers(ENDR_INI, ENDR_END)
            return ENDR_INI, ENDR_END
            #print("set pointers", ENDR_INI, ENDR_END,self.overlay_table)
        elif action == 1:
            print("activate overlay ",overlay_n)
            self.mvn.offset(self.get_end_pointer())
            self.add_overlay(overlay_n)
            saveCI = self.mvn.CI
            self.mvn.load(f'overlay{overlay_n}.hex', goto=saveCI-1)
            self.mvn.offset(0)

        elif action == 0:
            print("deactivate overlay ",overlay_n)
            self.remove_overlay()
            self.mvn.updateCI( self.mvn.CI - 1 )

    #=====================
    # Memória Admin
    #=====================
    def mem_acessar(self, endr):
        process = self.get_current_process()
        return self.adm_memory.acessar(process, endr)

    #=====================
    # Memória Paginada
    #=====================
    def randint_exclude(self, a, b, exclude):
        r = random.randint(a,b)
        while r in exclude:
            r = random.randint(a,b)
        return r

    def create_page(self, RAM, HD, pagen, pagesize):
        page = Page(RAM, HD, pagen, pagesize)
        return page

    def partitions(self, endr_ini, endr_end):
        """ Calcula os limites de cada página. """
        p = []
        if endr_end - endr_ini <= self.PAGE_SIZE:
            p = [(endr_ini, endr_end)]
            return p

        endr = endr_ini
        while endr+self.PAGE_SIZE < endr_end:
            p.append( (endr, endr+self.PAGE_SIZE-1) ) 
            endr += self.PAGE_SIZE
        p.append( (p[-1][1]+1, endr_end) )

        print(f":: Partição {p}")
        return p

    def keep_page(self, process):
        endr = process.CI
        ram_idx = process.get_page(endr).ram_pos
        self.keep_pages.add(ram_idx)
        return ram_idx

    def unkeep_page(self, ram_idx):
        self.keep_pages.remove(ram_idx)

    def page_pointers(self, idx):
        return slice(idx*self.PAGE_SIZE, (idx+1)*self.PAGE_SIZE)

    def get_page_process(self, page_obj):
        return self.ProcessList[page_obj.processID]

    def get_free_storage_idx(self):
        """ Escolhe uma posição livre do HD. """
        if not self.stored_pages:
            return 0

        a = min(self.stored_pages)
        b = max(self.stored_pages)

        if a == 0 and b == self.N_PAGES_STORAGE:
            return None

        for storage_idx in range(a-1,b+2):
            if storage_idx >= 0 and storage_idx < self.N_PAGES_STORAGE and (not self.stored_pages[storage_idx]):
                return storage_idx

    def page_allocate(self, process, page_num):
        ram_idx = self.randint_exclude(1,self.N_PAGES_RAM-1, self.keep_pages)
        storage_idx = None

        print(f":: Alocando processo <{process.ID}>, página <{page_num}> na ram <{ram_idx}>")

        # Se RAM está ocupada nessa posição, desocupa-la
        if self.loaded_pages[ram_idx]:
            # Escolhe posição livre no HD
            storage_idx = self.get_free_storage_idx()
            if storage_idx == None: pass
            # Guarda página que está ocupando a RAM na posição livre do HD
            ocup_page = self.loaded_pages[ram_idx]
            self.get_page_process(ocup_page).deallocate(storage_idx, ocup_page.virtual_pos)
            # Escreve a página <page_num> na RAM
        
        self.loaded_pages[ram_idx] = process.allocate(ram_idx, page_num)
        print(self.loaded_pages[ram_idx].isloaded)

        return ram_idx, storage_idx

    def process_page_load(self, process, endr):
        """ Carrega a página do CI do processo na RAM. """
        # Posições para alocação
        page_num = process.get_page_num(endr)
        ram_idx, storage_idx = self.page_allocate(process, page_num)

        # Se houver página ocupando ram_idx, guarda ela em storage_idx
        if storage_idx != None:
            print(":: Garantindo carregamento")
            self.byte_swap(ram_idx, storage_idx)
        else:
            print("E agora?")


    def byte_swap(self, ram_idx, storage_idx):
        """ Troca uma página da ram com a memória secundária. """
        ram_ptr = self.page_pointers(ram_idx)
        ram_bytes = self.mvn.MEM[ram_ptr]

        hd_ptr = self.page_pointers(storage_idx)
        hd_bytes = self.mvn.HD[hd_ptr]

        # SWAP bytes
        self.mvn.MEM[ram_ptr] = hd_bytes
        self.mvn.HD[hd_ptr] = ram_bytes

    def write_page(self, ram_idx, endr_ini, endr_end):
        """ Ativa o loader para escrever uma página de bytes na RAM. """
        print(f":: Escrevendo página em RAM <{ram_idx}>")

        # Ajusta offset do load e encontra endr limite
        self.mvn.reg_offset = (ram_idx)*self.PAGE_SIZE - endr_ini
        
        # Carrega na memória RAM
        self.mvn.state = 1
        while self.mvn.reg_loading and self.last_endr_loaded < endr_end:
            self.mvn.run_step()

        # Se houver instrução sobressalente, volta atrás com buffer
        if self.last_endr_loaded > endr_end:
            erase = self.last_endr_loaded
            offset = self.mvn.reg_offset
            print("::: Instru sobressalente", erase, offset)
            self.mvn.deleteBytes(self.last_endr_loaded + self.mvn.reg_offset, self.last_bytes_loaded)
            self.mvn.buffer_back(self.last_bytes_loaded*2 + 8)

        self.mvn.reg_offset = 0

    def do_page_table(self, endr):
        """ Realiza a conversão do endereço virtual para o endereço da memória física. """
        if endr < self.PAGE_SIZE:
            return endr
        else:
            process = self.get_current_process()

            # Mapeia o endereço do operando para memória física
            map_endr = process.get_CI(endr)

            # Caso o endereço não esteja, carregá-lo
            if map_endr == None:
                print("Não está carregado")
                self.process_page_load(process, endr)

            map_endr = process.get_CI(endr)

            print(f"    {endr:04X}(virtual) -> {map_endr:04X}(fisico)")
            return map_endr

    def initialize_pages(self):
        self.VIRTUAL_SPACE = 65536
        self.PAGE_SIZE = 256
        self.N_PAGES_VIRTUAL = int(self.VIRTUAL_SPACE/self.PAGE_SIZE)
        self.N_PAGES_RAM = int(len(self.mvn.MEM)/self.PAGE_SIZE)
        self.N_PAGES_STORAGE = int(len(self.mvn.HD)/self.PAGE_SIZE)

    #=====================
    # Administrador de Processos
    #=====================
    def get_current_process(self):
        return self.current_process

    def new_processID(self):
        ''' Retorna o menor id de processo disponível. '''
        ids = self.ProcessList.keys()
        if not ids:
            return 0

        N = max(ids)
        for k in range(N+1):
            if not k in ids:
                return k
        return N+1

    def create_process(self, tipo, payload):
        # Cria process control block
        processID = self.new_processID()
        process = ProcessControlBlock(processID, tipo)
        self.ProcessList[processID] = process

        if tipo == 0: # Código
            pass

        elif tipo == 1: # Dispositivo
            parameters = payload
            process.dispositivo(parameters)

        return process

    def destroy_process(self):
        # Garbage collect
       pass 

    def load_program(self, filepath):
        print("\n\n:: Carregando programa")
        self.mvn.load_buffer(filepath)
        print(":: Buffer >", self.mvn.buffer)

        # Recarrega os limites
        self.mvn.CI = 0x10
        for _ in range(11):
            self.mvn.state = 1
            self.mvn.run_step()

        # Limites
        ini = self.mvn.readPointer(0x5)
        end = self.mvn.readPointer(0x7)
        l = (end - ini)
        print(f':: {ini:04X} {end:04X} size:{l} bytes')

        # Calcula número de páginas
        npages = 1 + l//self.PAGE_SIZE
        print(f":: Tamanho de <{npages}> página.")

        # Cria processo
        process = self.create_process(0, None)
        print(f":: Processo <{process.ID}> criado.")

        # Cria as páginas 
        for page_num in range(1,npages+1):
            page = self.create_page(self.mvn.MEM, self.mvn.HD, page_num, self.PAGE_SIZE)
            page.processID = process.ID
            process.pages[page_num] = page
            print(f":: Criando pagina <{page_num}>")

        # Alocação de páginas em posição aleatória
        partitions = self.partitions(ini, end)

        for page_num in range(1, npages+1):
            print(f"::===========\n:: Alocando pagina <{page_num}>")

            # Posições para alocação
            ram_idx, storage_idx = self.page_allocate(process, page_num)

            # Se houver página ocupando ram_idx, guarda ela em storage_idx
            if storage_idx != None:
                print(f":: Conflito de páginas <{ram_idx},{storage_idx}>")
                self.byte_swap(ram_idx, storage_idx)

            # Com a posição de ram livre, escreve a página na ram
            page_ini, page_end = partitions[page_num - 1]
            self.write_page(ram_idx, page_ini, page_end)

            print(":: Fim do carregamento da página")
            print(":: DUMP:")
            print(self.mvn.dump(ini*ram_idx, ini*ram_idx + self.PAGE_SIZE))
        
        print(f":: Resumo: {npages} páginas alocadas. ")

        # Pointer to first instruction
        process.CI = ini

        print("::\n\n")

    #=====================
    # Administração dispositivos
    #=====================

    def registrar_dispositivo(self, process, tipo):
        parametros = None
        if tipo == 0: # Mouse
            parametros = {'tempo_processmento':3}
        elif tipo == 1: # Impressora 
            parametros = {'tempo_processmento':10, 'ocupado':False}
        elif tipo == 2: # Teclado
            parametros = {'tempo_processmento':5}

        # Coloca o dispositivo na lista de dispositivos
        self.dispositivos.append( process.dispositivo(parametros) )

    def elapsed_time(self, dispositivo):
        return self.time - dispositivo.last()

    #=====================
    # Multiprogramação
    #=====================
    def multiprog(self):
        for id in self.ProcessList.keys():
            process = self.ProcessList[id]

            if process.state == 0: continue # Pula processos finalizados

            # Recupera dados do processo
            self.current_process = process
            self.mvn.state = process.state

            # Recupera o CI atual do processo,
            self.mvn.CI = process.get_CI()

            # Se a página não estiver carregada
            # na memória, carrega-la.
            if self.mvn.CI == None:
                self.process_page_load(process, process.CI)
                self.mvn.CI = process.get_CI()
                
            # Mantem a página em execução fixa
            keep_ram_idx = self.keep_page(process)

            # Execute
            self.mvn.AC = process.AC
            self.mvn.run_step()

            # Libera a página de estar fixa
            self.unkeep_page(keep_ram_idx)

            # Check for end
            if self.mvn.state == 0:
                self.garbage.append(id)
                print(f"Processo <{id}> terminou. ")

            # Save
            process.state = self.mvn.state 
            process.set_CI(self, self.mvn.CI)
            process.AC = self.mvn.AC 

    #=====================
    # Executar código
    #=====================
    def run(self):
        running = True
        while running:
            self.multiprog()

            # Remove processos não utilizados
            if self.garbage:
                while len(self.garbage) > 0:
                    id = self.garbage.pop()
                    print(f":: Garbage collector -> Processo {id}")
                    del self.ProcessList[id]

            running = self.ProcessList

mvn = Simulador()
so = SistemaOperacional(mvn)

# Load program
so.load_program('print10.hex')
print("Páginas carregadas\n",so.loaded_pages)
print("Processos\n",so.ProcessList,"\n")

# Run
so.run()