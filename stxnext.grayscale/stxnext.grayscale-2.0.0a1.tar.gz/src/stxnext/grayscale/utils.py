# -*- coding:utf-8 -*-
import os
import re
import urlparse
from PIL import Image
from StringIO import StringIO
from zExceptions import NotFound

from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.Five import BrowserView
from Products.PythonScripts.PythonScript import PythonScript
try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite
from plone.app.blocks.transform import IncludeTiles
from plone.app.theming.utils import getCurrentTheme
from plone.app.theming.transform import ThemeTransform
from zope.component import queryMultiAdapter
from zope.contentprovider.interfaces import ContentProviderLookupError

from stxnext.grayscale import log
from stxnext.grayscale.config import TYPE, THEME

COLOR_PATTERN = re.compile(r"(?<=[:\s])#[a-fA-F0-9]{6}|(?<=[:\s])#[a-fA-F0-9]{3}(?=[\s;\"\'])|rgba?\(.+?\)|color:\s*(?!rgb)[a-z]+", re.M | re.I)
IMG_SRC_PATTERN = re.compile(r"<\s*img\s+[^>]*src\s*=\s*[\"']?([^\"' >]+)[\"']", re.I)
CSS_URL_PATTERN = re.compile(r"""url\(["']?([^\)'"]+)['"]?\)""", re.I)

# most popular css color names and their grayscale versions in css notation.
KWRD_MAP = {
    'blue': '#1d1d1d',
    'gray': '#808080',
    'green': '#969696',
    'orange': '#8c8c8c',
    'purple': '#555555',
    'red': '#4c4c4c',
    'silver': '#c0c0c0',
    'yellow': '#aaaaaa',
}


def add_param_to_url(url):
    """
    Adds "&grayscale=1" param to the url
    """
    url = list(urlparse.urlsplit(url))
    if url[3]:
        url[3] += '&grayscale=1'
    else:
        url[3] = 'grayscale=1'
    return urlparse.urlunsplit(url)


def transform_img_src(text):
    """
    Adds "grayscale=1" param to the ULR in src attribute in <img> tags to avoid
    caching images
    """
    urls = IMG_SRC_PATTERN.findall(text)
    for url in urls:
        new_url = add_param_to_url(url)
        text = text.replace(url, new_url)
    return text


def transform_css_url(text):
    """
    Adds "grayscale=1" param to the URL in url() directive in CSS to avoid
    caching images
    """
    urls = CSS_URL_PATTERN.findall(text)
    for url in urls:
        new_url = add_param_to_url(url)
        text = text.replace(url, new_url)
    return text


def transform_style_properties(text):
    """
    Converts the occurances of the color definitions
    to gray scale equivalents
    """
    matches = COLOR_PATTERN.findall(text)
    for match in set(matches):
        converted_match = transform_value(match)
        text = text.replace(match, converted_match)
    return text


def transform_value(color_str):
    """
    Transforms a single color value given
    in any string format to a relevant grayscale
    representation.
    """
    color_val = color_str.split(':')[-1].lower().strip(' ;')
    if color_val in KWRD_MAP:
        return 'color: %s' % KWRD_MAP[color_val]
    elif not color_str.startswith('color'):
        if color_val.startswith('#'):
            tup_val = hex_to_tuple(color_val)
        elif color_val.startswith('rgba'):
            return rgba_grayscale(color_val)
        elif color_val.startswith('rgb'):
            tup_val = rgb_to_tuple(color_val)
        else:
            return color_str
        return tuple_to_hex(grayscale_tuple(tup_val))
    else:
        return color_str


def grayscale_tuple(tup):
    """
    Takes a 3-tuple and returns a 3-tuple,
    with the valu of the input color converted
    to grayscale
    """
    try:
        gray = 0.299 * tup[0] + 0.587 * tup[1] + 0.114 * tup[2]
        gray = int(round(gray))
    except (IndexError, TypeError):
        raise ValueError("input %s is not in (r, g, b) format" % str(tup))
    return (gray, gray, gray)


def hex_to_tuple(text):
    """
    Transform #rrggbb notation of color
    to 3-tuple (r, g, b)
    """
    colorstring = text.strip()
    # remove trailing "#"
    colorstring = colorstring.lstrip('#')
    if len(colorstring) == 3:
        r, g, b = (colorstring[0] * 2, colorstring[1] * 2, colorstring[2] * 2)
    elif len(colorstring) == 6:
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    else:
        raise ValueError("input #%s is not in #RRGGBB format" % colorstring)
    return tuple([int(x, 16) for x in (r, g, b)])


def rgb_to_tuple(text):
    """
    Transforms rgb(x,x,x) both in decimal and %
    notation of color to 3-tuple (r, g, b)
    """
    numbers = re.findall(r'\d+', text)
    if '%' in text:
        tup = tuple([int((int(x) / 100.0) * 255) for x in numbers])
    else:
        tup = tuple([int(x) for x in numbers])
    return tup


def rgba_grayscale(text):
    """
    Replaces x, y, z colors in rgba(x,y,z,a) with coresponding grayscale values
    """
    tup_val = rgb_to_tuple(text)
    rgb_grayscale_tup = grayscale_tuple(tup_val[:3])
    if not tup_val[3:5]:
        raise ValueError("input %s is not in rgba(x,y,z,a) format" % text)
    alpha = float('.'.join([str(n) for n in tup_val[3:5]]))
    rgba_grayscale_tup = rgb_grayscale_tup + (alpha, )
    return "rgba(%d, %d, %d, %.1f)" % rgba_grayscale_tup


def tuple_to_hex(tup):
    """
    Transforms 3-tuple with colors to
    #RRGGBB html notation.
    """
    return '#%02x%02x%02x' % tup


def image_to_grayscale(image_data, path):
    """
    Converts image data to grayscale using PIL library
    """
    try:
        imagestring = StringIO(image_data)
        image_file = Image.open(imagestring)
        converted = image_file.convert('RGBA')
        converted = converted.convert('LA')
        res = StringIO()
        converted.save(res, format='PNG')
        return res.getvalue()
    except IOError, err:
        log.error('Error while transforming image: %s : %s' % (path, err))
        return image_data


def add_bodyclass(html_text):
    """
    Applies the 'gray-scale' css class on body tag
    """
    bodymatches = re.findall(r"<body.*>", html_text, re.I)
    for bodytag in bodymatches:
        if 'class' in bodytag:
            for css_classs in re.findall(r"""class\s*=\s*[\'\"]([-\w ]*)[^>]*>""", bodytag, re.I):
                modified_bodytag = bodytag.replace(css_classs,
                    ' '.join(('gray-style', css_classs)))
        else:
            modified_bodytag = bodytag.replace('>', ' class="gray-style">')
        html_text = html_text.replace(bodytag, modified_bodytag)
    return html_text


def get_resource(request, response, filename):
    """
    Returns the data of the resource cached
    in the file system
    """
    site = getSite()
    cached_file = site.restrictedTraverse(str('/++%s++%s/%s' % (
        TYPE, THEME, filename.strip('/'))))
    try:
        return cached_file(REQUEST=request, RESPONSE=response).read()
    except TypeError:
        return


def store_resource(path, data):
    """
    Stores the data of the resource in the
    file system
    """
    site = getSite()
    location = site.restrictedTraverse(str('/++%s++%s' % (TYPE, THEME))).directory

    if '/' in path:
        path, filename = path.rsplit('/', 1)
        dir_path = os.path.join(location, path.strip('/'))
        if not os.path.exists(dir_path):
            try:
                os.makedirs(os.path.normpath(dir_path))
            except OSError:
                log.error("Unable to create directory: %s" % path)
                return False
    else:
        filename = path
        dir_path = location

    file_path = os.path.join(dir_path, filename)
    fs_file = open(file_path, "w")
    try:
        fs_file.write(data)
    except TypeError:
        pass
    finally:
        fs_file.close()


def render_object_html(obj, request):
    """
    Returns rendered html for given content object
    """
    published = request.get('PUBLISHED')
    if isinstance(published, (BrowserView, FSPageTemplate, PythonScript)):
        if getCurrentTheme():
            transform = ThemeTransform(published, request)
            try:
                themed = transform.transformUnicode(published(), 'utf-8')
                tile_transform = IncludeTiles(published, request)
                tiled = tile_transform.transformIterable(themed, 'utf-8')
                if tiled:
                    return tiled.serialize()
            except Exception, error:
                log.error("Problem with transforming object %s: %s" % (published, error))
                return published()
        else:
            try:
                return published() or ''
            except NotFound:
                log.error("Resource '%s' not found" % repr(obj))
                return ''

    def_page_id = obj.getDefaultPage()
    if def_page_id:
        def_page = obj[def_page_id]
        return render_object_html(def_page, request)

    view_name = obj.getLayout()
    view = queryMultiAdapter((obj, request), name=view_name)
    if view:
        try:
            return view.context() or ''
        except ContentProviderLookupError:
            pass

    view = obj.restrictedTraverse(view_name, None)
    if view:
        try:
            return view.context() or ''
        except AttributeError:
            return view() or ''

    try:
        return obj()
    except AttributeError:
        pass
    return ''
