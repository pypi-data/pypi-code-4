from attribute_getter import AttributeGetter

class Resource(AttributeGetter):
    def __init__(self, gateway, attributes):
        AttributeGetter.__init__(self, attributes)
        self.gateway = gateway
                