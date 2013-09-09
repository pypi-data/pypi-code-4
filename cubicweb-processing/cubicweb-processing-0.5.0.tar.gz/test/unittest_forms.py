# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from cubicweb.devtools.testlib import CubicWebTC

from cubes.processing.views.forms import RunEditForm

class RunFormsTC(CubicWebTC):

    xpath_hidden_pdef = ('input[ starts-with(@name, "param_def-subject:") and '
                         '@type="hidden" ]')

    def setup_database(self):
        self.exe_eid = self.request().create_entity("Executable",
                                                    name=u"exe").eid

    def build_view(self):
        """Build the Run creation view"""
        req = self.request(__linkto='executable:%s:subject' % self.exe_eid)
        return self.view('creation', req=req, template=None, etype='Run')

    def test_build_view(self):
        """Basic check from the build_view method"""
        html = self.build_view()
        els = html.etree.xpath(
            '//select[starts-with(@name, "executable-subject")]')
        # No executable selector
        self.assertEqual(len(els), 0)
        # There must be NO '+ add a ParameterValue' link
        els = html.etree.xpath('//a[ starts-with(@href, '
                               '"javascript: addInlineCreationForm(" ) ]')
        self.assertEqual(len(els), 0)
        # There must be no "normal" ParamValue field
        els = html.etree.xpath('//select[ starts-with(@name, '
                               '"param_def-subject:")]')
        self.assertEqual(len(els), 0)

    def test_creation_linkto_noparam(self):
        html = self.build_view()
        # There must be no parameter value field
        els = html.etree.xpath('//' + self.xpath_hidden_pdef)
        self.assertEqual(len(els), 0)

    def test_creation_linkto_params(self):
        for vtype in (u'Float', u'Int', u'String', u'File'):
            # add a parameter of each type
            self.request().create_entity("ParameterDefinition",
                                         name=u"p" + vtype,
                                         param_type=u"input",
                                         value_type=vtype,
                                         parameter_of=self.exe_eid)
        html = self.build_view()
        # There must be one field per parameter definition
        els = html.etree.xpath('//' + self.xpath_hidden_pdef)
        self.assertEqual(len(els), 4)

    def test_unregister(self):
        self.request().create_entity("ParameterDefinition", name=u"p",
                                     param_type=u"input", value_type=u"File",
                                     parameter_of=self.exe_eid)
        try:
            self.vreg['forms'].unregister(RunEditForm)
            html = self.build_view()
            # There must be no parameter value field
            els = html.etree.xpath('//' + self.xpath_hidden_pdef)
            self.assertEqual(len(els), 0)
        finally:
            # Restore vreg in any case
            self.vreg['forms'].register(RunEditForm)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
