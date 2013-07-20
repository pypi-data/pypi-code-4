"""
Ax_FuzzyTourney - configuration component classes.

This module is not intended for public use.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------



# ----------------------------------------------------------------------------


class Component:
    pass

class Function(Component):
    def __init__(self):
        self.function_id = ''
        self.function = None
        self.config = {}
        self.app_context = {}


# ----------------------------------------------------------------------------


class Tournament(Component):
    def __init__(self):
        self.name = ""
        self.desc = ""
        self.input = Input()
        self.select = Select()
        self.output = Output()
        self.criteria = Criteria()
        self.judges = Judges()

class Select(Function):
    def __init__(self):
        Function.__init__(self)

class Input(Function):
    def __init__(self):
        Function.__init__(self)

class Output(Function):
    def __init__(self):
        Function.__init__(self)
        self.fields = []

class OutputField(Function):
    def __init__(self):
        Function.__init__(self)

class Criterion(Component):
    def __init__(self):
        self.id = ''
        self.name = ""
        self.init = 0.0
        self.desc = ""

class Criteria(Component):
    def __init__(self):
        self.criteria = []
    def get_by_id(self, id):
        for c in self.criteria:
            if c.id == id:
                return c
        return None

class Judges(Component):
    def __init__(self):
        self.judges = []

class Judge(Component):
    def __init__(self):
        self.name = ""
        self.desc = ""
        self.heuristics = []

class Heuristic(Component):
    def __init__(self):
        self.name = ""
        self.desc = ""
        self.lens = Lens()
        self.criterion_id = ""
        self.maps = []
        self.reduce = Reduce()
        self.reduced_maps = []

class Lens(Function):
    def __init__(self):
        Function.__init__(self)
        self.id = ''

class Map(Function):
    def __init__(self):
        Function.__init__(self)

class Reduce(Function):
    def __init__(self):
        Function.__init__(self)


