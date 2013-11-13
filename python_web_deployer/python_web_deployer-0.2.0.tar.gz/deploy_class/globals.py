class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class NotOveroadedError(Exception):
    pass

def singleton(cls, memory = {}):
    def _ins(*a, **k):
        if not cls.__name__ in memory:
            memory[cls.__name__] = cls(*a, **k)
        return memory[cls.__name__]
    return _ins