from tokenize import generate_tokens
from cStringIO import StringIO

class Token(object):
    type = None
    value = None
    def __repr__(self):
        return str((self.type, self.value))
        
class Tokenizer(object):
    def __init__(self, data):
        self.line = 0
        self.column = 0
        self.data = data
        self.index = -1
        self.tokens = []
        self.tokens = list(generate_tokens(StringIO(data).readline))
        self._has_next = True
        self.ntokens = len(self.tokens)
        
    def read_id(self):
        name = []
        while self.has_next():            
            token = self.next_token(False)   
            if token.type == 1:
                name.append(token.value)
                if self.readahead().value != '.':
                    break
            elif token.value =='.':
                name.append(token.value)
            else:
                self.backtrack()
                break
        return ''.join(name)                
      
    def backtrack(self):            
        self.index -= 1
        
    def readahead(self):
        toknum, tokval, a, b, c  = self.tokens[self.index]
        t = Token()
        t.type = toknum
        t.value = tokval
        t.line = 1
        return t
        
    def skip(self, index=1, line=0):
        self.index += index
        self.line += line
        
    def has_next(self):
        return self.index < self.ntokens
    
    def current_token(self):
        toknum, tokval, a, b, c  = self.tokens[self.index]
        t = Token()
        t.type = toknum
        t.value = tokval
        t.line = 1
        self.tokens.append(t)
        return t
    
    def skipnl(self):
        while self.index < self.ntokens: 
            toknum, tokval, a, b, c  = self.tokens[self.index]
            
            if tokval =="\n":
                self.line += 1
                self.index += 1
                continue
            else:
                return toknum, tokval, a, b, c
                
    def next_token(self, skipnl=True):
        ''' If skipnl is True, skips new line characters.
        '''
        if skipnl:
            toknum, tokval, a, b, c = self.skipnl()
            self.index += 1
        else:
            toknum, tokval, a, b, c  = self.tokens[self.index]
            self.index += 1
        startl, startc = a
        endl, endc = b

        t = Token()
        t.type = toknum
        t.start = a
        t.end = b
        t.value = tokval
        t.line = 1
        return t
        