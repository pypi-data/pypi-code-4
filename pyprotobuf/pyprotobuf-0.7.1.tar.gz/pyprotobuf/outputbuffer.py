from cStringIO import StringIO

class OutputBuffer(object):
    def __init__(self):
        self.file = StringIO()
        
    def write(self, string):
        self.file.write(string)
        
    def to_string(self):
        return self.file.getvalue()
