from action_gateway import ActionGateway
from achievement_gateway import AchievementGateway
from game_gateway import GameGateway
from player_gateway import PlayerGateway
from purchase_gateway import PurchaseGateway

class GamerocketGateway(object):
    def __init__(self, config):
        self.config = config
        self.achievement = AchievementGateway(self)
        self.action = ActionGateway(self)
        self.game = GameGateway(self)
        self.player = PlayerGateway(self)
        self.purchase = PurchaseGateway(self)