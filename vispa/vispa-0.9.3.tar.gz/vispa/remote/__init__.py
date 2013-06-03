import rpyc

class Service(rpyc.Service):
    def on_connect(self):
        pass
    
    def on_disconnect(self):
        pass

    def exposed_getmodule(self, name):
        """imports an arbitrary module"""
        return __import__(name, None, None, "*", -1)
