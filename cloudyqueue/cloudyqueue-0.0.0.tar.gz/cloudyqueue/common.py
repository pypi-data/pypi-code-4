
class Message:
    def __init__(self, valeu
    def value

class AbstractQueue:
    
    def next(self):
        return QueueElement(self)

    def read(self):
        raise NotImplemented

    def write(self, message):
        raise NotImplemented
    
    def delete(self, message):
        raise NotImplemented
        
        
