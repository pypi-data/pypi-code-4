

__author__ = 'yarnaid'

try:
    import tools.convertion as convert
    import pixelmap
    import properties
except:
    import glespy.tools.convertion as convert
    import glespy.pixelmap as pixelmap
    import glespy.properties as properties


class Alm(properties.Multipoled):

    name = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        try:
            return super(Alm, self).__setattr__(name, value)
        except:
            self.__dict__[name] = value
        return value

    def to_map(self, map_name=None, **kwargs):
        map_name = convert.alm_to_map(self.name, map_name=map_name, **kwargs)
        attrs = kwargs.copy()
        attrs['name'] = map_name
        pmap = pixelmap.gPixelMap(**attrs)
        return pmap

    def smooth(self, smooth_window, **kwargs):
        smoothed_name = convert.tools.get_out_name(
            out_name=kwargs.get('smoothed_name'),
            suffix='alm_smoothed.fit'
        )
        smoothed_name = convert.smooth_alm(
            self.name,
            smooth_window,
            smoothed_name=smoothed_name,
            **kwargs
        )
        kwargs['name'] = smoothed_name
        alm_smoothed = Alm(**kwargs)
        self.name = smoothed_name
        return alm_smoothed

    def rotate(self, **kwargs):
        rotated_name = convert.rotate_alm(self.name, **kwargs)
        self.__dict__.update(kwargs)
        self.name = rotated_name
        return self.name
