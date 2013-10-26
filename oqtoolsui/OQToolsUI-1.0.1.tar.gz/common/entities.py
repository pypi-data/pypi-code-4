class Gmpe:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __str__(self):
        return self.name + "(" + str(self.weight) + ")"

    def __repr__(self):
        return self.__str__()