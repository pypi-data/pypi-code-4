
from copy import deepcopy

""" Some helper methods for schema manipulation """

def invisibleFields(schema, *fields):
    """ makes a list of fields invisible """
    for name in fields:
        schema[name].widget.visible = False


