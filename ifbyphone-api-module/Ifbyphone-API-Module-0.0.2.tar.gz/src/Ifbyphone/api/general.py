from base import IfbyphoneApiBase

class General(IfbyphoneApiBase):

    def building_blocks(self):
        """ Get a list of all available building blocks
        """
        self.options['action'] = 'general.buildingblockids'
        return self.call(self.options)