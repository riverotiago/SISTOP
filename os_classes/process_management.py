class ProcessControlBlock():
    def __init__(self, id):
        self.id = id
        self.ID = 0
        self.CI = 0
        self.AC = 0
        self.state = 1
        self.MEMLIMIT = None

    