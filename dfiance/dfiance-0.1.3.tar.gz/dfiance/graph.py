import vertigo

class TypeGraphNode(vertigo.GraphNode):
    '''GraphNode for an unbound dfiance type graph.'''
    def __init__(self, dfier):
        self.dfier = dfier

    @property
    def value(self):
        return self.dfier

    def key_iter(self):
        return self.dfier.sub_dfier_keys()

    def _get_child(self, key):
        return TypeGraphNode(self.dfier.sub_dfier(key))

class BoundTypeGraphNode(vertigo.GraphNode):
    '''GraphNode for a bound dfiance type graph.'''
    def __init__(self, value, dfier=None):
        if dfier is None:
            dfier = type(value).dfier()
        self.dfier = dfier
        self.val = value

    @property
    def value(self):
        return self.dfier

    def key_iter(self):
        return self.dfier.sub_dfier_keys(self.val)

    def _get_child(self, key):
        dfier = self.dfier.sub_dfier(key, self.val)
        value = self.dfier.sub_value(self.val, key)
        return BoundTypeGraphNode(value, dfier)

class ValueGraphNode(vertigo.GraphNode):
    '''GraphNode for a dfiance type objects.'''
    def __init__(self, value, dfier=None):
        if dfier is None:
            dfier = type(value).dfier()
        self.dfier = dfier
        self.val = value

    @property
    def value(self):
        return self.val

    def key_iter(self):
        return self.dfier.sub_value_keys(self.val)

    def _get_child(self, key):
        dfier = self.dfier.sub_dfier(key, self.val)
        value = self.dfier.sub_value(self.val, key)
        return ValueGraphNode(value, dfier)
