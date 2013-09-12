import os
import inspect

class Environment(object):
    
    def __init__(self, server, port, is_ssl, ssl_certificate):
        self.__server = server
        self.__port = port
        self.is_ssl = is_ssl
        self.ssl_certificate = ssl_certificate
    
    @property
    def base_url(self):
        return self.protocol + self.server_and_port
    
    @property
    def port(self):
        return int(self.__port)
    
    @property
    def protocol(self):
        if self.__port == "443":
            return "https://"
        else:
            return "http://"
    
    @property
    def server(self):
        return self.__server
    
    @property
    def server_and_port(self):
        return self.__server + ":" + self.__port
    
    @staticmethod
    def gamerocket_root():
        return os.path.dirname(inspect.getfile(Environment))

Environment.Development = Environment("localhost", os.getenv("GATEWAY_PORT") or "8280", False, None)
Environment.Production = Environment("api.gamerocket.io", "443", True, Environment.gamerocket_root() + "/ssl/www_gamerocket_io.ca.crt")
