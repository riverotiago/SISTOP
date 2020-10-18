class ProcessTable():
    def __init__(self, id):
        self.id = id

        # Todo -> Transform these into attributes
        process_entry = {}
        process_entry['ID'] = 0
        process_entry['State'] = 'Ready'
        process_entry['CI'] = 0x0000
        process_entry['MemoryInfo'] = {}
        process_entry['MemoryInfo']['Limits'] = {}

    def new_entry(self):
        pass

    