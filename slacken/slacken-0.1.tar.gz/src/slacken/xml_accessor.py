""" Acessors for XML """
__author__ = 'Alistair Broomhead'

from xml.dom.minidom import NodeList
from slacken.dicttypes import AttrDict


class XMLAccessor(object):
    """ Wraps a dom element to allow attribute-style access """

    @classmethod
    def from_string(cls, text):
        """ Constructor from string """
        from xml.dom.minidom import parseString
        return cls(parseString(text))

    def to_dict(self, base_name='xml_accessor'):
        """
        :param base_name: root dictionary key
        """

        assert isinstance(self, XMLAccessor)

        def _set_tag(d, tag, data):
            d[tag] = data
            return d

        def _r(node, d, tag):
            try:
                return _set_tag(d, tag, node.data)
            except AttributeError:
                pass
            _d, _l = {}, []
            for n in node.childNodes:
                try:
                    _r(XMLAccessor(n), _d, n.tagName)
                except AttributeError:
                    _d_ = {}
                    _r(XMLAccessor(n), _d_, '')
                    _l.append(_d_[''])
            if _d:
                return _set_tag(d, tag, _d)
            if _l:
                if len(_l) == 1:
                    return _set_tag(d, tag, _l[0])
                return _set_tag(d, tag, _l)
            return _set_tag(d, tag, None)

        d = _r(self, {}, base_name)[base_name]
        return AttrDict(d)

    def __repr__(self):
        if isinstance(self.dom, NodeList):
            return "<XMLAccessor %r>" % [x.nodeName for x in self.dom]
        else:
            return "<XMLAccessor %r>" % self.dom.nodeName

    def __init__(self, dom):
        if isinstance(dom, NodeList) and len(dom) == 1:
            dom = dom[0]
        self.dom = dom

    def __getattr__(self, item):
        if isinstance(self.dom, NodeList):
            for node in self.dom:
                try:
                    return getattr(XMLAccessor(node), item)
                except BaseException:
                    pass
            from xml.dom import NotFoundErr

            raise NotFoundErr(item)
        else:
            try:
                node = self.dom.getElementsByTagName(item)
                if not node:
                    attrs = self.dom._attrs
                    return AttrDict(attrs)[item].nodeValue
                if isinstance(node, NodeList) and len(node) == 1:
                    node = node[0]
                return XMLAccessor(node)
            except BaseException:
                return getattr(self.dom, item)
