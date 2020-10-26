class Page():
    def __init__(self, RAM, HD, pagen, pagesize):
        self.RAM = RAM
        self.HD = HD
        self.virtual_pos = pagen
        self.PAGE_SIZE = pagesize
        self.isloaded = False
        self.isstored = False
        self.protected = False
        self.hd_pos = 0
        self.ram_pos = 0
        self.processID = None
        
    def getCode(self):
        if self.isloaded:
            return self.RAM[self.ram_pos:self.ram_pos+self.PAGE_SIZE]
        else:
            return self.HD[self.hd_pos:self.hd_pos+self.PAGE_SIZE]

    def getPointer(self):
        if self.isloaded:
            return self.ram_pos 
        else:
            return self.hd_pos 

    def setLoaded(self, offset):
        self.isloaded = True
        self.isstored = True
        self.ram_pos = offset*self.PAGE_SIZE

    def setStored(self, offset):
        self.isloaded = False
        self.isstored = True
        self.hd_pos = offset*self.PAGE_SIZE
