from configuration import Configuration
from resource import Resource

class Player(Resource):
    
    def __repr__(self):
        detail_list = ["id", "name", "emailHash", "locale", "totalPointsAchievement", "ticksRemaining", "lastActivity", "dynProp"]
        return super(Player, self).__repr__(detail_list)
    
    @staticmethod
    def create(params={}):        
        return Configuration.gateway().player.create(params)
    
    @staticmethod
    def delete(player_id):        
        return Configuration.gateway().player.delete(player_id)
    
    @staticmethod
    def find(player_id):
        return Configuration.gateway().player.find(player_id)
    
    @staticmethod
    def update(player_id, params={}):
        return Configuration.gateway().player.update(player_id, params)
    
    @staticmethod
    def create_signature():
        return ["id", "name", "emailHash", "locale", "totalPointsAchievement", "ticksRemaining", "lastActivity", "dynProp"]
    
    def __init__(self, gateway, attributes):
        Resource.__init__(self, gateway, attributes)