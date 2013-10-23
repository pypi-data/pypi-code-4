# encoding: utf-8
import xml.etree.ElementTree as ET


# Code is based on http://code.activestate.com/recipes/573463/
def _convert_dict_to_xml_recurse(parent, dictitem, listnames, attributenames):
    """Helper Function for XML conversion."""
    # we can't convert bare lists
    assert not isinstance(dictitem, list)

    if isinstance(dictitem, dict):
        for (tag, child) in sorted(dictitem.iteritems()):
            if isinstance(child, list):
                # iterate through the array and convert
                listelem = ET.Element(tag)
                parent.append(listelem)
                for listchild in child:
                    elem = ET.Element(listnames.get(tag, 'item'))
                    listelem.append(elem)
                    _convert_dict_to_xml_recurse(elem, listchild, listnames, attributenames)
            else:
                if tag in attributenames:
                    parent.attrib[tag] = unicode(child)
                else:
                    elem = ET.Element(tag)
                    parent.append(elem)
                    _convert_dict_to_xml_recurse(elem, child, listnames, attributenames)
    elif type(dictitem) == ET.Element:
        for i in list(dictitem):
            parent.append(i)
    elif not dictitem is None:
        parent.text = unicode(dictitem)


def mark_safe(str):
    """
    Convert string to an ElementTree.
    """
    return ET.fromstring('<wrapper>{0}</wrapper>'.format(str))


def dict2et(xmldict, roottag='data', listnames=None, attributenames=[]):
    """Converts a dict to an Elementtree.

    Converts a dictionary to an XML ElementTree Element::

    >>> data = {"nr": "xq12", "positionen": [{"m": 12}, {"m": 2}]}
    >>> root = dict2et(data)
    >>> ET.tostring(root)
    '<data><nr>xq12</nr><positionen><item><m>12</m></item><item><m>2</m></item></positionen></data>'

    >>> data = {"nr": "xq12"}
    >>> root = dict2et(data, attributenames=['nr'])
    >>> ET.tostring(root)
    '<data nr="xq12" />'

    >>> data = {"nr": "xq12", "content": mark_safe("<p><span>content data</span></p>")}
    >>> root = dict2et(data, attributenames=['nr'])
    >>> ET.tostring(root)
    '<data nr="xq12"><content><p><span>content data</span></p></content></data>'

    Per default ecerything ins put in an enclosing '<data>' element. Also per default lists are converted
    to collecitons of `<item>` elements. But by provding a mapping between list names and element names,
    you van generate different elements::

    >>> data = {"positionen": [{"m": 12}, {"m": 2}]}
    >>> root = dict2et(data, roottag='xml')
    >>> ET.tostring(root)
    '<xml><positionen><item><m>12</m></item><item><m>2</m></item></positionen></xml>'

    >>> root = dict2et(data, roottag='xml', listnames={'positionen': 'position'})
    >>> ET.tostring(root)
    '<xml><positionen><position><m>12</m></position><position><m>2</m></position></positionen></xml>'

    >>> data = {"kommiauftragsnr":2103839, "anliefertermin":"2009-11-25", "prioritaet": 7,
    ... "ort": u"Hücksenwagen",
    ... "positionen": [{"menge": 12, "artnr": "14640/XL", "posnr": 1},],
    ... "versandeinweisungen": [{"guid": "2103839-XalE", "bezeichner": "avisierung48h",
    ...                          "anweisung": "48h vor Anlieferung unter 0900-LOGISTIK avisieren"},
    ... ]}

    >>> print ET.tostring(dict2et(data, 'kommiauftrag',
    ... listnames={'positionen': 'position', 'versandeinweisungen': 'versandeinweisung'}))
    ...  # doctest: +SKIP
    '''<kommiauftrag>
    <anliefertermin>2009-11-25</anliefertermin>
    <positionen>
        <position>
            <posnr>1</posnr>
            <menge>12</menge>
            <artnr>14640/XL</artnr>
        </position>
    </positionen>
    <ort>H&#xC3;&#xBC;cksenwagen</ort>
    <versandeinweisungen>
        <versandeinweisung>
            <bezeichner>avisierung48h</bezeichner>
            <anweisung>48h vor Anlieferung unter 0900-LOGISTIK avisieren</anweisung>
            <guid>2103839-XalE</guid>
        </versandeinweisung>
    </versandeinweisungen>
    <prioritaet>7</prioritaet>
    <kommiauftragsnr>2103839</kommiauftragsnr>
    </kommiauftrag>'''

    >>> print ET.tostring(dict2et(data, 'kommiauftrag',
    ... listnames={'positionen': 'position', 'versandeinweisungen': 'versandeinweisung'},
    ... attributenames=['anliefertermin', 'prioritaet', 'kommiauftragsnr']))
    ...  # doctest: +SKIP
    '''<kommiauftrag anliefertermin="2009-11-25" prioritaet="7" kommiauftragsnr="2103839">
    <positionen>
        <position>
            <posnr>1</posnr>
            <menge>12</menge>
            <artnr>14640/XL</artnr>
        </position>
    </positionen>
    <ort>H&#xC3;&#xBC;cksenwagen</ort>
    <versandeinweisungen>
        <versandeinweisung>
            <bezeichner>avisierung48h</bezeichner>
            <anweisung>48h vor Anlieferung unter 0900-LOGISTIK avisieren</anweisung>
            <guid>2103839-XalE</guid>
        </versandeinweisung>
    </versandeinweisungen>
    </kommiauftrag>'''
    """

    if not listnames:
        listnames = {}
    root = ET.Element(roottag)
    _convert_dict_to_xml_recurse(root, xmldict, listnames, attributenames)
    return root


def dict2xml(xmldict, roottag='data', listnames=None, attributenames=[]):
    return ET.tostring(dict2et(xmldict, roottag, listnames, attributenames))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
