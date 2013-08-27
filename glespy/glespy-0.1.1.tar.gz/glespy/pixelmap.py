import os

__author__ = 'yarnaid'

try:
    import properties
    import tools.convertion as conv
except:
    import glespy.properties as properties
    import glespy.tools.convertion as conv

class gPixelMap(properties.Rendered):
    """
    Class with lmax, lmin, nx, np attributes for map rendering
    """
    name = None
    temp = None

    def __init__(self, **kwargs):
        # super(gPixelMap, self).__init__(**kwargs)
        if self.name:
            self.temp = False
        else:
            self.temp = True
        for k, v in kwargs.items():
            setattr(self, k, v)
        pass

    def unset_temp(self):
        self.temp = False

    def __setattr__(self, name, value):
        try:
            return super(gPixelMap, self).__setattr__(name, value)
        except:
            self.__dict__[name] = value

    def from_alm(self):
        pass

    def __del__(self):        # todo: test
        if self.temp:
            pass
            # os.remove(self.name)

    def show(self, **kwargs):
        # todo: test
        conv.show_map(self.name, **kwargs)

    def add_map(self, other, **kwargs):
        try:
            other_name = other.name
        except AttributeError:
            other_name = other
        except:
            raise ValueError('[{}]: unsupported other var type {}'.format(__name__, type(other)))
        self.name = conv.sum_map(self.name, other_name, **kwargs)

    def get_attrs(self):
        # todo: test
        return {'nx': self.nx,
                'np': self.np,
                'lmax': self.lmax,
                'lmin': self.lmin,
                }
