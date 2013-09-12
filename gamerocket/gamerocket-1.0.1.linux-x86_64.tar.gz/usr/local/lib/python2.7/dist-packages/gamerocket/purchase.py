from configuration import Configuration
from resource import Resource

class Purchase(Resource):
    
    def __init__(self, gateway, attributes):
        Resource.__init__(self, gateway, attributes)
    
    @staticmethod
    def find(id):
        return Configuration.gateway().purchase.find(id)
    
    @staticmethod
    def buy(id, attributes):
        return Configuration.gateway().purchase.buy(id, attributes)