
""" ``principal`` module.
"""


class Principal(object):
    """ Container of user specific security information
    """

    def __init__(self, id='', roles=(), alias='', extra=''):
        self.id = id
        self.roles = roles
        self.alias = alias
        self.extra = extra

    def dump(self):
        """ Dump principal object.
        """
        return '\x1f'.join([
            self.id,
            ';'.join(self.roles),
            self.alias,
            self.extra])

    @classmethod
    def load(cls, s):
        """ Load principal object from string.
        """
        id, roles, alias, extra = s.split('\x1f', 3)
        return cls(id, tuple(roles.split(';')), alias, extra)
