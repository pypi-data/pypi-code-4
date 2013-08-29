# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import os
import pkg_resources

from tw.api import Widget, JSLink, CSSLink, js_function

modname = __name__

def collect_variants(basedir, filename, modname):
    """
    Gathers the various variants of the ui-js-files.
    """
    normal_variant = "/".join([basedir, filename])
    if not pkg_resources.resource_exists(modname, normal_variant):
        raise Exception("No such resource: %s.%s" % (modname, normal_variant))
    res = dict(normal=normal_variant)
    filebase = os.path.splitext(filename)[0]
    min_filename = "%s.min.js" % filebase
    min_variant = "/".join([basedir, "minified", min_filename])
    if pkg_resources.resource_exists(modname, min_variant):
        res["min"] = min_variant

    for packed_name in ("packed", "pack"):
        for subdir in ("", "packed"):
            packed_filename = "%s.%s.js" % (filebase, packed_name)
            dir_ = basedir
            if subdir:
                dir_ = os.path.join(dir_, subdir)
            packed_variant = os.path.join(dir_, packed_filename)
            if pkg_resources.resource_exists(modname, packed_variant):
                res["packed"] = packed_variant

    if len(res.keys()) == 1:
        return res["normal"]
    return res


jquery_js = JSLink(modname=modname,
                   filename=dict(normal='static/javascript/jquery-1.5.js',
                                 min='static/javascript/jquery-1.5.min.js',
                                 ),
                   javascript=[])

jQuery = js_function('$')




def filter_resources(resource):
    """
    This is a `resource_aggregation_filter` implementation.

    It is supposed to be run by passing

      abl.jquery

    as part of the "-d"-parameter to the `aggregate_tw_resources`-command.
    It will filter out all the schemes and i18n-files under the abl.jquery-packages.
    """
    modname, filename = resource.modname, resource.active_filename()
    if modname is not None and modname.startswith("abl.jquery") and ("i18n" in filename or "theme" in filename):
        return False
    return True

