from base import Base
from utf8_pprint import PrettyPrinter

# Makes repr() a bit neater
pp = PrettyPrinter(indent=4)

class Read(Base):
    def __init__(self, api, path, params):
        self.response = None
        Base.__init__(self, api, path, params)

    def data(self):
        r = self.get_response()
        try:
            key = [k for k in r.keys() if k != 'header'][0]
            return self.get_response()[key]
        except IndexError:
            return ''

    def objects(self):
        return _dict2obj(self.data())

    def count(self):
        return self.get_response()['header']['count']

    def more(self):
        return self.get_response()['header']['more']

    def messages(self):
        return self.get_response()['header']['messages']

    def get_response(self):
        if not self.response:
            self.response = self.api.get(self)
        return self.response

def _dict2obj(d):
        if isinstance(d, list):
            d = [_dict2obj(x) for x in d]
        if not isinstance(d, dict):
            return d
        class C(object):
            pass
            
            def __repr__(self):
                return pp.pformat(self.__dict__)

        o = C()
        for k in d:
            o.__dict__[k] = _dict2obj(d[k])
        return o

