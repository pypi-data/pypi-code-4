

class Colors:

    HEADER  = '\033[95m'
    OKBLUE  = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    END     = '\033[0m'

    def __init__(self):
        pass

    def disable(self):
        self.HEADER  = ''
        self.OKBLUE  = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL    = ''
        self.END     = ''


class Message:
    def __init__(self):
        pass

    @staticmethod
    def fail(message):
        print Colors.FAIL + message + Colors.END

    @staticmethod
    def ok(message):
        print Colors.OKGREEN + message + Colors.END

    @staticmethod
    def warning(message):
        print Colors.WARNING + message + Colors.END
