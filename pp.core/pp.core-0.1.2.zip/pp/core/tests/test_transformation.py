# -*- encoding=utf-8 -*-

################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

from pp.core import transformation 

@transformation.registerTransformation
def dummy_cleanup(root):
    for node in root.xpath('//p'):
        try:
            del node.attrib['foo']
        except KeyError:
            pass

def test_cleanup_transformation():
    T = transformation.Transformer(['dummy_cleanup'])
    HTML = u'<p foo="bar">hello world - üöäß</p>'
    html = T(HTML)
    assert html == u'<p>hello world - üöäß</p>'

def test_xpath_query():
    names = ('h1', 'h2')
    assert transformation.xpath_query(names) == './/*[name()="h1" or name()="h2"]'

def test_availableTransformations():
    assert transformation.availableTransformations() == ['dummy_cleanup']
