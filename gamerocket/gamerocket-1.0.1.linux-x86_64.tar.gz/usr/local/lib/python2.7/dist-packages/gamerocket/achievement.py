from configuration import Configuration
from resource import Resource

class Achievement(Resource):
    
    def __init__(self, gateway, attributes):
        Resource.__init__(self, gateway, attributes)
    
    @staticmethod
    def find(player_id, id, attributes):
        return Configuration.gateway().achievement.find(player_id, id, attributes)
        