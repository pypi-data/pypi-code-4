# -*- coding: latin1 -*- vim: sw=4 ts=8 sts=4 si et 
"""
Konversion von Farbangaben
"""

__version__ = (0,
               3,   # add_colour_option, hsl(), hsla()
               #    # TODO: improve error handling and/or help
               'rev-%s' % '$Rev: 907 $'[6:-2],
               )
__all__ = [# Data:
           'HTML4_COLOURS',
           'SVG_COLOURS',
           'CSS_COLOURS',
           # Exceptions:
           'InvalidColourSpec',
           'InvalidColourValue',
           'PercentageExpected',
           # for colour conversion: 
           'css_intclip',
           'css_alphaclip',
           'parse_colour',
           'parse_alpha_colour',
           # for optparse; will likeliy move to opo.py:
           ## 'add_colour_option',
           ## 'cb_factory',
           ]

from optparse import OptParseError, OptionValueError

HTML4_COLOURS = {   # http://www.w3.org/TR/css3-color/#html4
        'black':   (0,     0,   0),
        'silver':  (192, 192, 192),
        'gray':    (128, 128, 128),
        'white':   (255, 255, 255),
        'maroon':  (128,   0,   0),
        'red':     (255,   0,   0),
        'purple':  (128,   0, 128),
        'fuchsia': (255,   0, 255),
        'green':   (0,   128,   0),
        'lime':    (0,   255,   0),
        'olive':   (128, 128,   0),
        'yellow':  (255, 255,   0),
        'navy':    (0,     0, 128),
        'blue':    (0,     0, 255),
        'teal':    (0,   128, 128),
        'aqua':    (0,   255, 255), 
        }
SVG_COLOURS = {     # http://www.w3.org/TR/css3-color/#svg-color 
        'aliceblue':            (240, 248, 255),
        'antiquewhite':         (250, 235, 215),
        'aquamarine':           (127, 255, 212),
        'azure':                (240, 255, 255),
        'beige':                (245, 245, 220),
        'bisque':               (255, 228, 196),
        'blanchedalmond':       (255, 235, 205),
        'blueviolet':           (138,  43, 226),
        'brown':                (165,  42,  42),
        'burlywood':            (222, 184, 135),
        'cadetblue':            (95,  158, 160),
        'chartreuse':           (127, 255,   0),
        'chocolate':            (210, 105,  30),
        'coral':                (255, 127,  80),
        'cornflowerblue':       (100, 149, 237),
        'cornsilk':             (255, 248, 220),
        'crimson':              (220,  20,  60),
        'cyan':                 (0,   255, 255),
        'darkblue':             (0,     0, 139),
        'darkcyan':             (0,   139, 139),
        'darkgoldenrod':        (184, 134,  11),
        'darkgray':             (169, 169, 169),
        'darkgreen':            (0,   100,   0),
        'darkgrey':             (169, 169, 169),
        'darkkhaki':            (189, 183, 107),
        'darkmagenta':          (139,   0, 139),
        'darkolivegreen':       (85,  107,  47),
        'darkorange':           (255, 140,   0),
        'darkorchid':           (153,  50, 204),
        'darkred':              (139,   0,   0),
        'darksalmon':           (233, 150, 122),
        'darkseagreen':         (143, 188, 143),
        'darkslateblue':        (72,   61, 139),
        'darkslategray':        (47,   79,  79),
        'darkslategrey':        (47,   79,  79),
        'darkturquoise':        (0,   206, 209),
        'darkviolet':           (148,   0, 211),
        'deeppink':             (255,  20, 147),
        'deepskyblue':          (0,   191, 255),
        'dimgray':              (105, 105, 105),
        'dimgrey':              (105, 105, 105),
        'dodgerblue':           (30,  144, 255),
        'firebrick':            (178,  34,  34),
        'floralwhite':          (255, 250, 240),
        'forestgreen':          (34,  139,  34),
        'gainsboro':            (220, 220, 220),
        'ghostwhite':           (248, 248, 255),
        'gold':                 (255, 215,   0),
        'goldenrod':            (218, 165,  32),
        'greenyellow':          (173, 255,  47),
        'grey':                 (128, 128, 128),
        'honeydew':             (240, 255, 240),
        'hotpink':              (255, 105, 180),
        'indianred':            (205,  92,  92),
        'indigo':               (75,    0, 130),
        'ivory':                (255, 255, 240),
        'khaki':                (240, 230, 140),
        'lavender':             (230, 230, 250),
        'lavenderblush':        (255, 240, 245),
        'lawngreen':            (124, 252,   0),
        'lemonchiffon':         (255, 250, 205),
        'lightblue':            (173, 216, 230),
        'lightcoral':           (240, 128, 128),
        'lightcyan':            (224, 255, 255),
        'lightgoldenrodyellow': (250, 250, 210),
        'lightgray':            (211, 211, 211),
        'lightgreen':           (144, 238, 144),
        'lightgrey':            (211, 211, 211),
        'lightpink':            (255, 182, 193),
        'lightsalmon':          (255, 160, 122),
        'lightseagreen':        (32,  178, 170),
        'lightskyblue':         (135, 206, 250),
        'lightslategray':       (119, 136, 153),
        'lightslategrey':       (119, 136, 153),
        'lightsteelblue':       (176, 196, 222),
        'lightyellow':          (255, 255, 224),
        'limegreen':            (50,  205,  50),
        'linen':                (250, 240, 230),
        'magenta':              (255,   0, 255),
        'mediumaquamarine':     (102, 205, 170),
        'mediumblue':           (0,     0, 205),
        'mediumorchid':         (186,  85, 211),
        'mediumpurple':         (147, 112, 219),
        'mediumseagreen':       (60,  179, 113),
        'mediumslateblue':      (123, 104, 238),
        'mediumspringgreen':    (0,   250, 154),
        'mediumturquoise':      (72,  209, 204),
        'mediumvioletred':      (199,  21, 133),
        'midnightblue':         (25,   25, 112),
        'mintcream':            (245, 255, 250),
        'mistyrose':            (255, 228, 225),
        'moccasin':             (255, 228, 181),
        'navajowhite':          (255, 222, 173),
        'oldlace':              (253, 245, 230),
        'olivedrab':            (107, 142,  35),
        'orange':               (255, 165,   0),
        'orangered':            (255,  69,   0),
        'orchid':               (218, 112, 214),
        'palegoldenrod':        (238, 232, 170),
        'palegreen':            (152, 251, 152),
        'paleturquoise':        (175, 238, 238),
        'palevioletred':        (219, 112, 147),
        'papayawhip':           (255, 239, 213),
        'peachpuff':            (255, 218, 185),
        'peru':                 (205, 133,  63),
        'pink':                 (255, 192, 203),
        'plum':                 (221, 160, 221),
        'powderblue':           (176, 224, 230),
        'rosybrown':            (188, 143, 143),
        'royalblue':            (65,  105, 225),
        'saddlebrown':          (139,  69,  19),
        'salmon':               (250, 128, 114),
        'sandybrown':           (244, 164,  96),
        'seagreen':             (46,  139,  87),
        'seashell':             (255, 245, 238),
        'sienna':               (160,  82,  45),
        'skyblue':              (135, 206, 235),
        'slateblue':            (106,  90, 205),
        'slategray':            (112, 128, 144),
        'slategrey':            (112, 128, 144),
        'snow':                 (255, 250, 250),
        'springgreen':          (0,   255, 127),
        'steelblue':            (70,  130, 180),
        'tan':                  (210, 180, 140),
        'thistle':              (216, 191, 216),
        'tomato':               (255,  99,  71),
        'turquoise':            (64,  224, 208),
        'violet':               (238, 130, 238),
        'wheat':                (245, 222, 179),
        'whitesmoke':           (245, 245, 245),
        'yellowgreen':          (154, 205,  50),
        }
SVG_COLOURS.update(HTML4_COLOURS)
CSS_COLOURS = SVG_COLOURS


class InvalidColourSpec(ValueError):
    pass
class InvalidColourValue(InvalidColourSpec):
    pass
class PercentageExpected(InvalidColourValue):
    pass

def clip_percent2float(s):
    if isinstance(s, basestring):
        if not s.endswith('%'):
            raise PercentageExpected(s)
        else:
            s = float(s[:-1])
    res = float(s) / 100
    if res <= 0.0:
        return 0.0
    elif res >= 1.0:
        return 1.0
    else:
        return res

def clip_hue(val):
    """
    >>> clip_hue('400')
    40
    >>> clip_hue(-120)
    240
    """
    if not isinstance(val, int):
        val = int(val)
    if 0 <= val < 360:
        return val
    return ((val % 360) + 360) % 360

def float2i255(fl):
    """
    >>> float2i255(0.5)
    128
    >>> float2i255(1.0)
    255
    """
    res = int(fl * 256 + 0.5)
    if res >= 255:
        return 255
    elif res <= 0:
        return 0
    else:
        return res

def _hue2rgb(m1, m2, h):
    """
    helper for hsl2rgb
    """
    if h < 0:
        h += 1
    if h > 1:
        h -= 1
    if h * 6 < 1:
        return m1 + (m2 - m1) * h * 6
    if h * 2 < 1:
        return m2
    if h * 3 < 2:
        return m1 + (m2 - m1) * (2.0 / 3 - h) * 6
    return m1


def hsl2rgb(hue, saturation, lightness):
    """
    convert a hsl spec. to (red, green, blue), with [0 ... 255] values

    hue - mapped to the colour circle [0 ... 360) (e.g. -120 -> 240)
    saturation - a percentage (0: grey; 100: fully coloured)
    lightness - a percentage (0: black; 100: white)

    >>> hsl2rgb(120, 50, 0)
    (0, 0, 0)
    >>> hsl2rgb(120, 100, 50)
    (0, 255, 0)
    >>> hsl2rgb(0, 100, 25)
    (128, 0, 0)
    >>> hsl2rgb(180, 100, 50)
    (0, 255, 255)
    >>> hsl2rgb(120, 50, 100)
    (255, 255, 255)
    """
    h = float(clip_hue(hue)) / 360
    s = clip_percent2float(saturation)
    l = clip_percent2float(lightness)
    # print h, s, l
    if l <= 0.5:
        m2 = l * (s + 1)
        # print l + s - l * s
    else:
        m2 = l + s - l * s
        # print l * (s + 1)
    # print m2
    m1 = l * 2 - m2
    return tuple(map(float2i255,
                     [_hue2rgb(m1, m2, h+1.0/3),
                      _hue2rgb(m1, m2, h),
                      _hue2rgb(m1, m2, h-1.0/3),
                      ]))

def css_intclip(val):
    """
    for colour parsing according to CSS rules:
    - convert percentages to integer values
    - clip integer values to the range [0 ... 255]

    >>> css_intclip('-1')
    0
    >>> css_intclip('300')
    255
    >>> css_intclip(300)
    255
    >>> css_intclip('100%')
    255
    >>> css_intclip('50%')
    128
    """
    if isinstance(val, int):
        res = val
    elif val.endswith('%'):
        res = int(float(val[:-1]) * 256 / 100
                  + 0.5)
    else:
        res = int(val)
    if res <= 0:
        return 0
    elif res >= 255:
        return 255
    else:
        return res

def css_alphaclip(val):
    """
    for colour parsing according to CSS rules:
    - clip float values to the range [0.0 ... 1.0]

    >>> css_alphaclip('-1')
    0.0
    >>> css_alphaclip('1.1')
    1.0
    >>> css_alphaclip(1.1)
    1.0
    """
    if isinstance(val, float):
        res = val
    else:
        res = float(val)
    if res <= 0.0:
        return 0.0
    elif res >= 1.0:
        return 1.0
    else:
        return res

def parse_colour(val, func=css_intclip):
    """
    return a (red, green, blue) 3-tuple for the given colour spec.
    
    val - the parsed value
    func - the factory function, by default: -> css_intclip

    >>> parse_colour('lime')
    (0, 255, 0)
    >>> parse_colour('rgb(1, 2, 3)')
    (1, 2, 3)
    >>> parse_colour('#aabbcc')
    (170, 187, 204)
    >>> parse_colour('#abc')
    (170, 187, 204)
    >>> parse_colour('1,2,3')
    (1, 2, 3)
    """
    # TODO: hsl(hue, saturation, lightness) values; http://www.w3.org/TR/css3-color/#hsl-color
    v = val.strip().lower()
    if v in CSS_COLOURS.keys():
        return CSS_COLOURS[v]
    elif v.startswith('#'):
        length = len(v)
        if length not in (4, 7):
            raise ValueError('%(val)r: 3 or 6 hex. digits expected'
                             % locals())
        if length == 4:
            return tuple([int(ch*2, 16) for ch in list(v[1:])])
        else:
            return tuple([int(s, 16)
                          for s in (v[1:3], v[3:5], v[5:])])
    elif v.startswith('rgb('):
        if not v.endswith(')'):
            raise ValueError("%(val)r: closing ')' expected"
                             % locals())
    elif v.startswith('hsl('):
        if not v.endswith(')'):
            raise ValueError("%(val)r: closing ')' expected"
                             % locals())
        tup = hsl2rgb(*tuple(v[4:-1].split(',')))
    else:
        raise ValueError(v)
    if len(tup) != 3:
        length = len(tup)
        raise ValueError('%(val)r yielded %(length)d values %(tup)r'
                         '; 3 expected'
                         % locals())
    return tup
parse_color = parse_colour

def parse_alpha_colour(val, func=css_intclip, opacity=1.0):
    """
    return a (red, green, blue, opacity) 4-tuple

    val - the parsed value
    func - the int. factory function, see -> css_intclip
    opacity - the default opacity, if some other form than rgba(...) given

    >>> parse_alpha_colour('rgba(50%,50%,50%,0.3)')
    (128, 128, 128, 0.3)
    >>> parse_alpha_colour('rgba(50%,50%,50%,0.3)', opacity=None)
    (128, 128, 128, 0.3)
    >>> parse_alpha_colour('rgb(50%,50%,50%)', opacity=None)
    (128, 128, 128, None)
    >>> parse_alpha_colour('#abc')
    (170, 187, 204, 1.0)
    >>> parse_alpha_colour('#abc', opacity=None)
    (170, 187, 204, None)
    """
    # TODO: hsla(hue, saturation, lightness, alpha) values; http://www.w3.org/TR/css3-color/#hsla-color
    v = val.strip().lower()
    if v.startswith('rgba('):
        if not v.endswith(')'):
            raise ValueError("%(val)r: closing ')' expected"
                             % locals())
        tup = tuple(v[5:-1].split(','))
        if len(tup) != 4:
            length = len(tup)
            raise ValueError('%(val)r yielded %(length)d values %(tup)r'
                             '; 4 expected'
                             % locals())
        opa = css_alphaclip(tup[3])
        return tuple(map(func, tup[:3])) + (opa,)
    elif v.startswith('hsla('):
        if not v.endswith(')'):
            raise ValueError("%(val)r: closing ')' expected"
                             % locals())
        tup = tuple(v[5:-1].split(','))
        if len(tup) != 4:
            length = len(tup)
            raise ValueError('%(val)r yielded %(length)d values %(tup)r'
                             '; 4 expected'
                             % locals())
        s = 'hsl(%s)' % ','.join(tup[:3])
        print s
        return parse_colour(s) + \
                (css_alphaclip(tup[3]),)
    else:
        if opacity is not None:
            opa = css_alphaclip(opacity)
        else:
            opa = None
        return parse_colour(val, func) + (opa,)
parse_alpha_color = parse_alpha_colour

def normalhex(str):
    """
    expand 'abc' to 'aabbcc' (convert 3-character-hexadecimal spec
    into its 6-character equivalent)

    >>> normalhex('abc')
    'aabbcc'
    >>> normalhex('aabbcc')
    'aabbcc'
    """
    str = str.lower()
    if len(str) == 3:
        return ''.join(map(lambda s:2*s, list(str)))
    return str

def x2d(str):
    """
    Konvertiert eine beliebige vorzeichenlose Sedezimalzahl (ein String)

    >>> x2d('a')
    10
    """
    return int(str, 16)

def splitcolour(str):
    """
    split a hex. colour spec. into 3 strings

    >>> splitcolour('abc')
    ['aa', 'bb', 'cc']
    """
    if len(str) == 3:
        return map(lambda s:2*s, list(str))
    elif len(str) == 6:
        res = list()
        while str:
            res.append(str[:2])
            str = str[2:]
        return res
    else:
        raise InvalidColourValue(str)

def shortesthex(tup):
    """
    >>> shortesthex((0, 0, 255))
    '00f'
    >>> shortesthex((0, 0, 0))
    '000'
    >>> shortesthex((1, 2, 3))
    '010203'
    """
    assert isinstance(tup, tuple)
    longhex = (3 * '%02x') % tup
    shorthex = (longhex[0], longhex[2], longhex[4])
    comp = ''.join([2*ch for ch in shorthex])
    if comp == longhex:
        return ''.join(shorthex)
    else:
        return longhex


def cascade(str, astuple=0):
    """
    generate the conversion cascade for the given spec

    str -- the colour spec (symbolic names are allowed)

    astuple -- if True, the final generated element is returned as a 3-tuple
               of integers rather than a string

    >>> list(cascade('magenta'))
    ['magenta', '#f0f', '#ff00ff', 'rgb(255, 0, 255)']
    """
    s = str.lower().strip()
    if s.startswith('#'):
        s = s[1:]
    if s in CSS_COLOURS.keys():
        yield s
        s = shortesthex(CSS_COLOURS[s])
    try:
        if len(s) == 3:
            yield '#'+s
        tup = splitcolour(s)
        yield '#' + ''.join(tup)
        rgb = map(x2d, tup)
        if not astuple:
            rgb = 'rgb(%d, %d, %d)' % tuple(rgb)
        yield rgb
    except KeyError:
        raise InvalidColourSpec

def print_cascade(str):
    """
    print the conversion cascade for the given spec
    """
    try:
        print '\t-> '.join(list(cascade(str)))
    except InvalidColourSpec:
        print u'%s:\tkeine gültige Farbangabe' % str

def comp(d1, d2):
    """
    comparison function for the colours list (print_table)
    """
    return cmp(d1['sort'], d2['sort'])

def comp2(d1, d2):
    """
    comparison function for the colours list (--print)
    """
    return cmp(d1['name'], d2['name'])

def print_table():
    print '<table style="empty-cells:show"><thead><tr>'
    print '  <th scope="col">Name</th>'
    print '  <th scope="col">Ansicht</th>'
    print '  <th scope="col">hex</th>'
    print '  <th scope="col" class="r">rot</th>'
    print '  <th scope="col" class="g">gr&uuml;n</th>'
    print '  <th scope="col" class="b">blau</th>'
    print '  <th scope="col">rgb()</th>'
    print '</tr></thead><tbody>'
    colours.sort(comp)
    for dic in colours:
        dic['hex'] = normalhex(dic['hex'])
        dic['r'], dic['g'], dic['b'] = CSS_COLOURS[dic['name']]
        print '<tr>'
        print '  <th scope="row">%(name)s</th>' % dic
        print '  <td style="background-color:#%(hex)s"></td>' % dic
        print '  <td class="hex">%(hex)s</td>' % dic
        print '  <td class="r">%(r)d</td>' % dic
        print '  <td class="g">%(g)d</td>' % dic
        print '  <td class="b">%(b)d</td>' % dic
        print '  <td><tt>rgb(%(r)d, %(g)d, %(b)d)</tt></td>' % dic
        print '</tr>'
    print '</tbody></table>'

def extract_dest(*args):
    """
    >>> extract_dest('-a', '--aa-bb')
    'aa_bb'
    """
    for a in args:
        if not a.startswith('--'):
            continue
        if a[2:]:
            if a[2] == '-':
                raise OptParseError('invalid option: %r'
                                    % a)
            return a[2:].replace('-', '_')

def cb_factory(option, opt_str, value, parser,
               func, **kwargs):
    try:
        setattr(parser.values, option.dest,
                func(value, **kwargs))
    except ValueError, e:
        raise OptionValueError(str(e))

def add_colour_option(parser, *args, **kwargs):
    """
    create an option which takes a CSS colour specification

    alpha - if True, a 4-tuple will be created (red, green, blue, alpha);
            in this case, you should give an 'opacity' argument as well
            and/or create an --opacity option (which is mentioned in the
            default help text)
    opacity - a default value for hex, keyword or rgb/hsl specs which don't
              yield an alpha value; 0.0 means full transparency, 1.0 full opacity
    help - if None (default), a matching help text will be used;
           use another False value to suppress the help
    """
    defaults = {'dest':     None,
                'factory':  None,
                'help':     None,
                'metavar':  None,
                'action':   'callback',
                'type':     'string',
                'callback': cb_factory,
                'alpha':    0,
                'opacity':  None,
                }
    defaults.update(kwargs)
    func = defaults.pop('factory')
    alpha = defaults.pop('alpha')
    opacity = defaults.pop('opacity')
    if func is None:
        func = alpha and parse_alpha_colour or parse_colour
    defaults['callback_kwargs'] = dict(func=func)
    if defaults['help'] is None:
        if alpha:
            if opacity is None:
                defaults['help'] = _('any valid CSS colour specification'
                        ', including rgba(...) and hsl[a](...);'
                        ' if not rgba(...) nor hsla(...), specify'
                        ' --opacity as well')
            else:
                opacity = css_alphaclip(opacity)
                defaults['help'] = _('any valid CSS colour specification'
                        ', including rgba(...) and hsl[a](...);'
                        ' if not rgba(...) nor hsla(...), '
                        'the opacity value is %(opacity)f or --opacity'
                        ) % locals()
            defaults['callback_kwargs']['opacity'] = opacity
        else:
            defaults['help'] = _('any valid CSS colour specification'
                    ', including rgb(...) and hsl(...)')
    elif not defaults['help']:
        del defaults['help']
    if defaults['metavar'] is None:
        defaults['metavar'] = alpha and 'rgba(...)' or 'rgb(...)'
    elif not defaults['metavar']:
        del defaults['metavar']

    a = tuple(args) or ('--colour', '--color')
    if defaults['dest'] is None:
        defaults['dest'] = extract_dest(*a)
    if defaults['dest'] is None:
        raise OptParseError('no destination given')
    return parser.add_option(*a, **defaults)


if __name__ == '__main__':
    try:
        from thebops.enhopa import OptionParser, OptionGroup
    except ImportError:
        from optparse import OptionParser, OptionGroup
    import sys
    from thebops.modinfo import main as modinfo
    from thebops.errors import warn

    parser = OptionParser(usage='%prog [COLORSPEC] [...] | [Optionen]',
                          version='%%prog %s'
                          % ''.join(map(str, __version__)))

    try:
        parser.set_collecting_groupX()
    except AttributeError:
        pass
    group_ = OptionGroup(parser, 'Tabellen ausgeben')
    group_.add_option('--print',
                      action='store_true',
                      dest='print_raw',
                      help='Gibt die bekannten Farbwerte aus'
                      )
    group_.add_option('--html',
                      action='store_true',
                      dest='print_html',
                      help='Generiert eine HTML-Farbtabelle'
                      ' zur Standardausgabe')
    group_.add_option('--svg-colours', '--svg-colors',
                      action='store_true',
                      dest='svg_colours',
                      help=u'Liste auch die von SVG übernommenen und '
                      'in CSS3 enthaltenen Farbnamen')
    add_colour_option(group_)
    add_colour_option(group_, '--alpha-colour', alpha=1)
    parser.add_option_group(group_)

    option, args = modinfo(parser=parser)

    ok = 0
    def headline(txt):
        from sys import stderr
        global ok
        print >> stderr, txt
        print >> stderr, '~' * len(txt)
        ok = 1

    _ORDER = ['fuchsia', 'purple', 'maroon', 'red', 'yellow',
              'lime', 'green', 'olive', 'teal', 'aqua', 'blue', 'navy',
              'black', 'gray', 'silver', 'white']
    def makekey(n):
        try:
            return (_ORDER.index(n),) + HTML4_COLOURS[n]
        except ValueError:
            return (1000,) + SVG_COLOURS[n]
    if option.print_html or option.print_raw:
        colours = []
        for name, tup in (option.svg_colours
                          and SVG_COLOURS
                          or  HTML4_COLOURS).items():
            colours.append({
                'name': name,
                'hex': shortesthex(tup),
                'sort': makekey(name),
                })
    if option.colour:
        headline('--colour')
        print option.colour
    if option.alpha_colour:
        headline('--alpha-colour')
        print option.alpha_colour
    if option.print_html:
        headline('--html')
        if args:
            warn('Argument(e) %s wird/werden ignoriert' % (tuple(args),))
        print_table()
    elif option.print_raw:
        headline('--print')
        if args:
            warn('Argument(e) %s wird/werden ignoriert' % (tuple(args),))
        colours.sort(comp2)
        done = set()
        for dic in colours:
            name = dic['name']
            if name not in done:
                print_cascade(name)
                done.add(name)
    if args:
        headline('Argumente')
        for a in args:
            print_cascade(a)
    if not ok:
        try:
            print_cascade(raw_input('Eine Farbangabe eingeben: '))
        except KeyError:
            print

