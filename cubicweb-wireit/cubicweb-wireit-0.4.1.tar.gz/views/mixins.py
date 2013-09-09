# copyright 2012-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

'''mixins shared by several views'''

from json import dumps, loads

from cubicweb.web import stdmsgs
from cubicweb.web.formwidgets import Button


class WiringViewMixin(object):
    '''mixin to be used to display a wiring inside a wireit editor interface'''

    css = ('wireit/lib/yui/assets/skins/sam/skin.css',
           'wireit/lib/inputex/css/inputEx.css',
           'wireit/css/WireIt.css',
           'wireit/css/WireItEditor.css',
           'cw_wiring_editor.css',
           )
    js = ('wireit/lib/yui/utilities/utilities.js',
          'wireit/lib/yui/resize/resize-min.js',
          'wireit/lib/yui/layout/layout-min.js',
          'wireit/lib/yui/container/container-min.js',
          'wireit/lib/yui/json/json-min.js',
          'wireit/lib/yui/button/button-min.js',
          'wireit/lib/yui/tabview/tabview-min.js',
          'wireit/lib/inputex/js/inputex.js',
          'wireit_patches/lib/inputex/js/Field.js',
          'wireit_patches/js/util/inputex/WirableField-beta.js',
          'wireit/lib/inputex/js/Group.js',
          'wireit/lib/inputex/js/Visus.js',
          'wireit/lib/inputex/js/fields/StringField.js',
          'wireit/lib/inputex/js/fields/NumberField.js',
          'wireit/lib/inputex/js/fields/Textarea.js',
          'wireit/lib/inputex/js/fields/SelectField.js',
          'wireit/lib/inputex/js/fields/EmailField.js',
          'wireit/lib/inputex/js/fields/UrlField.js',
          'wireit/lib/inputex/js/fields/ListField.js',
          'wireit/lib/inputex/js/fields/CheckBox.js',
          'wireit/lib/inputex/js/fields/InPlaceEdit.js',
          'wireit_patches/lib/inputex/js/fields/FileField-beta.js',
          'wireit/js/WireIt.js',
          'wireit/js/CanvasElement.js',
          'wireit/js/Wire.js',
          'wireit_patches/js/Terminal.js',
          'wireit/js/util/DD.js',
          'wireit/js/util/DDResize.js',
          'wireit_patches/js/Container.js',
          'wireit/js/Layer.js',
          'wireit/js/util/inputex/FormContainer-beta.js',
          'wireit/js/LayerMap.js',
          'wireit_patches/js/WiringEditor.js',
          'wireit/js/ImageContainer.js',
          'wireit/js/InOutContainer.js',
          )

    template = """
<div id="wireiteditor" class="%(css)s">
    <div id="left">
        <div id="modules"></div>
        <div class="section">
            <div class="iformTitle">
                <span>%(minimap)s</span>
            </div>
            <div style="position: relative; margin-top: 0.5em">
                <div id="layerMap"></div>
            </div>
        </div>
        <div class="section">
            %(wiring_descr)s
        </div>
    </div>
    <div id="center"></div>
</div>
"""

    def add_media(self):
        self._cw.add_js('cw_wiring_editor.js')
        self._cw.add_js(('jq_upload/js/jquery.iframe-transport.js',
                         'jq_upload/js/vendor/jquery.ui.widget.js',
                         'jq_upload/js/jquery.fileupload.js',))
        for css in self.css:
            self._cw.add_css(self._cw.data_url(css), localfile=False)
        for js in self.js:
            self._cw.add_js(self._cw.data_url(js), localfile=False)
        if self._cw.ie_browser():
            self._cw.add_js('excanvas.js')

    def html(self, wiring, wlang, editable, cancel_url):
        'return view html structure'
        ctx = {'css': 'editable' if editable else 'readonly',
               'minimap': self._cw._('minimap'),
               'wiring_descr': self.wiring_descr_html(wiring, wlang, editable),
               }
        return self.template % ctx

    def wiring_descr_html(self, wiring, wlang, editable):
        'this is the place where you can add a html description of the entity'
        return u''

    def set_wlang_permissions(self, wlang, editable):
        '''return wiring language `wlang` json description modified to
        graphically show edition is not possible'''
        json = wlang.cw_adapt_to('wireit.json').json
        if editable:
            return json
        descr = loads(json)
        for module in descr['modules']:
            for field in module['container']['fields']:
                field['inputParams']['disabled'] = True # disallow field edition
                field['inputParams']['editable'] = False # disallow terminal edition
        return dumps(descr)

    def set_wiring_edit_permissions(self, wiring, globally_editable):
        """ hook to allow fine-tuning the editability of the langage itself """
        return wiring.cw_adapt_to('wireit.json').json

    def setup_editor(self, wiring, wlang, editable=False, cancel_url='/'):
        'setup the entire wireit editor'
        self.add_media()
        self.w(self.html(wiring, wlang, editable, cancel_url))
        wlang_json = self.set_wlang_permissions(wlang, editable)
        try:
            eid = int(wiring.eid)
        except ValueError: # entity creation
            eid = None
        json_wiring = self.set_wiring_edit_permissions(wiring,
                                                       globally_editable=editable)
        ctx = {'wiring_eid': dumps(eid),
               'wiring_json': dumps(json_wiring or '{}'),
               'lang_eid': dumps(wlang.eid),
               'lang_json': dumps(wlang_json),}
        self._cw.add_onload('cw.wireiteditor_setup(%(wiring_eid)s, %(wiring_json)s, '
                            '%(lang_eid)s, %(lang_json)s);' % ctx)
