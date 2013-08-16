import _helper
import colour

class Color(object):
    def __init__(self, w, x, y, z):
        self._w = w
        self._x = x
        self._y = y
        self._z = z
        self._convert()

    def _convert(self):
        """ Override this to convert w,x,y,z values into color local values """
        pass

    @property
    def hex(self):
        """ Override this to convert to an RGB hex string """
        if hasattr(self, "_rgb"):
            (r,g,b) = self._rgb
            return "{0:02X}{1:02X}{2:02X}".format(r,g,b)

        return "Unknown!"

    @classmethod
    def from_adobe(cls, color_space, w, x, y, z):
        if color_space in _SPACE_MAPPER:
            return _SPACE_MAPPER[color_space](w,x,y,z)

    @property
    def colorspace(self):
        return type(self).__name__[1:-5]

    @property
    def value(self):
        """ Override to display color value """
        return ""

    def __repr__(self):
        return "<Color colorspace={0} value={1}>".format(
            self.colorspace,
            self.value
        )

class _RGBColor(Color):
    def _convert(self):
        self._r = int(self._w/256)
        self._g = int(self._x/256)
        self._b = int(self._y/256)

    @property
    def value(self):
        mapping = (
           ("r", self._r),
           ("g", self._g),
           ("b", self._b),
        )
        return " ".join(("{0}={1:02X}".format(x,y) for x,y in mapping))

    @property
    def hex(self):
        return "".join(map(
            "{0:02X}".format, (self._r, self._g, self._b)
        ))
        
class _HSBColor(Color):
    def _convert(self):
        self._h = int(self._w/182.04)
        self._s = int(self._x/655.35)
        self._b = int(self._y/655.35)

    @property
    def value(self):
        mapping = (
           ("h", self._h),
           ("s", self._s),
           ("b", self._b),
        )
        return " ".join(("{0}={1:d}".format(x,y) for x,y in mapping))

    def _map(self, i, t, p, q, brightness):
        mapper = (
            (brightness, t, p),
            (q, brightness, p),
            (p, brightness, t),
            (p, q, brightness),
            (t, p, brightness),
            (brightness, p, q)
        )
        if (i > len(mapper)):
            data = mapper[-1]
        else:
            data = mapper[i]
        return data

    @property
    def _rgb(self):
        h = self._h/360.0
        s = self._s/100.0
        b = self._b/100.0

        return map(lambda x: int(x*255.0), colour.hsl2rgb((h,s,b)))

class _CMYKColor(Color): pass
class _LabColor(Color): pass
class _GrayColor(Color): pass
class _WideCMYKColor(Color): pass

_SPACE_MAPPER = {
    0: _RGBColor,
    1: _HSBColor,
    2: _CMYKColor,
    7: _LabColor,
    8: _GrayColor,
    9: _WideCMYKColor
}
