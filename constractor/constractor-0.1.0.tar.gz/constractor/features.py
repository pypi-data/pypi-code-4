# -*- coding: utf-8 -*-

# Copyright (C) 2013, David Kuryakin (dkuryakin@gmail.com)
#
# This material is provided "as is", with absolutely no warranty expressed
# or implied. Any use is at your own risk.
#
# Permission to use or copy this software for any purpose is hereby granted
# without fee. Permission to modify the code and to distribute modified
# code is also granted without any restrictions.

class Feature(object):
    '''
    Feature object have two attributes:
    1) document - dict.
    2) elements - list of dict.

    Detailed information about this attributes:
        elements[i] => {
            'x': int,
            'y': int,
            'height': int,
            'width': int,
            'outer_html': unicode,
            'inner_html': unicode,
            'plain_text': unicode,
            'tag': unicode,
            'classes': [unicode, ...],
            'attributes': {unicode: unicode, ...},
            'childs': int,
            'sibling': int,
            'tot_childs': int,
            'link_texts': [unicode, ...],
            'element': QWebElement
        }

        document => {
            'inner_html': unicode,
            'plain_text': unicode,
            'title': unicode,
            'height': int,
            'width': int,
            'keywords': [unicode, ...],
            'description': unicode
        }
    '''

    def __init__(self, page_data):
        self.document = page_data['document']
        self.elements = page_data['elements']

    def features(self):
        features = []
        for element in self.elements:
            features.append(self.feature(element))
        return features

    def feature(self, element):
        pass


class RelativePointsCount(Feature):
    def feature(self, element):
        text = element['plain_text']
        N = len(text) or 1
        M = text.count(u'.')
        return float(M) / N


class ContentTagWeight(Feature):
    # TODO: Review following euristic weights!
    TAGS = {
        'BLOCKQUOTE': 0, 'OBJECT': 0, 'LINK': 0, 'BR': 0, 'OPTGROUP': 0, 'SUB': 0, 'PRE': 0, 'RP': 0, 'FRAME': 0,
        'METER': 0, 'SOURCE': 0, 'SECTION': 0, 'BODY': 1, 'TH': 0, 'FIGURE': 0, 'H1': 0, 'H2': 0, 'H3': 0, 'H4': 0,
        'H5': 0, 'H6': 0, 'FIGCAPTION': 0, 'P': 1, 'BASE': 0, 'TFOOT': 0, 'VAR': 0, 'AUDIO': 0, 'MAP': 0, 'OL': 0,
        'TEXTAREA': 0, 'ACRONYM': 0, 'MENU': 0, 'DT': 0, 'STYLE': 0, 'DIALOG': 0, 'ADDRESS': 0, 'OUTPUT': 0,
        'CODE': 0, 'HR': 0, 'SUP': 0, 'ASIDE': 0, 'LABEL': 0, 'META': 0, 'DEL': 0, 'FONT': 0, 'SELECT': 0,
        'NOFRAMES': 0, 'CENTER': 0, 'KBD': 0, 'BASEFONT': 0, 'HTML': 0, 'VIDEO': 0, 'ARTICLE': 1, 'EM': 0,
        'FRAMESET': 0, 'FIELDSET': 0, 'DATALIST': 0, 'BDO': 0, 'BDI': 0, 'PARAM': 0, 'S': 0, 'COMMAND': 0,
        'DETAILS': 0, 'PROGRESS': 0, 'INPUT': 0, 'EMBED': 0, 'CAPTION': 0, 'TRACK': 0, 'BUTTON': 0, 'SCRIPT': 0,
        'KEYGEN': 0, 'UL': 0, 'TIME': 0, 'STRIKE': 0, 'OPTION': 0, 'TITLE': 0, 'NAV': 0, 'RT': 0, 'SMALL': 0,
        'STRONG': 0, 'COL': 0, 'AREA': 0, 'APPLET': 0, 'TABLE': 1, 'B': 0, 'IMG': 0, 'SUMMARY': 0, 'DFN': 0,
        'RUBY': 0, 'SPAN': 1, 'MARK': 0, 'DL': 0, 'WBR': 0, 'DD': 0, 'TBODY': 1, 'DIV': 1, 'INS': 0, 'LEGEND': 0,
        'DIR': 0, 'NOSCRIPT': 0, 'COLGROUP': 0, 'BIG': 0, 'TT': 0, 'TR': 1, 'LI': 0, 'IFRAME': 0, 'TD': 1, 'A': 0,
        'HEAD': 0, 'FORM': 1, 'I': 0, 'Q': 0, 'HEADER': 0, 'U': 0, 'ABBR': 0, 'THEAD': 0, 'CANVAS': 0, 'FOOTER': 0,
        'SAMP': 0, 'CITE': 0
    }

    def feature(self, element):
        tag = element['tag']
        return float(self.TAGS.get(tag, 0.5))


class ContentClassWeight(Feature):
    # TODO: Review following euristic weights!
    TAGS = {
        'content': 1, 'article': 1, 'menu': 0, 'header': 0, 'footer': 0, 'comment': 0, 'meta': 0, 'footer': 0,
        'footnote': 0, 'foot': 0, 'post': 1, 'hentry': 1, 'entry': 1, 'text': 1, 'body': 1
    }

    def feature(self, element):
        for _class in element['classes']:
            for tag, weight in self.TAGS.iteritems():
                if tag.lower() in _class.lower():
                    return float(weight)
        return 0.5


class ContentIdWeight(ContentClassWeight):
    def feature(self, element):
        tag_id = element['attributes'].get(u'id', u'').lower()
        for tag, weight in self.TAGS.iteritems():
            if tag.lower() in tag_id:
                return float(weight)
        return 0.5


class TotalChildsPerSymbol(Feature):
    def feature(self, element):
        text = element['plain_text']
        text_len = len(text) or 1
        tot_childs = element['tot_childs']
        return float(tot_childs) / text_len


class ChildsPerSymbol(Feature):
    def feature(self, element):
        text = element['plain_text']
        text_len = len(text) or 1
        childs = element['childs']
        return float(childs) / text_len


class RelativeTextLength(Feature):
    def feature(self, element):
        el_len = len(element['plain_text'])
        doc_len = len(self.document['plain_text']) or 1
        return float(el_len) / doc_len


class LinkTextDensity(Feature):
    def feature(self, element):
        link_text = u''.join(element['link_texts'])
        link_text_len = len(link_text)
        text_len = len(element['plain_text']) or 1
        return float(link_text_len) / text_len


class LinkDensity(Feature):
    def feature(self, element):
        links = len(element['link_texts'])
        tot_childs = element['tot_childs'] or 1
        return float(links) / tot_childs


class RelativeArea(Feature):
    def feature(self, element):
        area = self.document['width'] * self.document['height'] or 1
        el_area = element['width'] * element['height']
        return float(el_area) / area


class RelativeWidth(Feature):
    def feature(self, element):
        w = self.document['width'] or 1
        el_w = element['width']
        return float(el_w) / w


class RelativeHeight(Feature):
    def feature(self, element):
        h = self.document['height'] or 1
        el_h = element['height']
        return float(el_h) / h


class InTheMiddleOfWidth(Feature):
    def feature(self, element):
        c = self.document['width'] / 2
        x = element['x']
        w = element['width']
        flag = x < c and (x + w) > c
        return float(flag)


class InTheMiddleOfHeight(Feature):
    def feature(self, element):
        c = self.document['height'] / 2
        y = element['y']
        h = element['height']
        flag = y < c and (y + h) > c
        return float(flag)


class ContainsH1(Feature):
    def feature(self, element):
        h1 = element['element'].findAll('h1')
        return float(len(h1) > 0)


class TextLengthVsHtmlLength(Feature):
    def feature(self, element):
        tl = len(element['plain_text'])
        hl = len(element['inner_html']) or 1
        return float(tl) / hl


class ImgsPerSymbol(Feature):
    def feature(self, element):
        imgs = len(element['element'].findAll('img'))
        symbols = len(element['plain_text']) or 1
        result = float(imgs) / symbols
        if result > 1.0:
            result = 1.0
        return result


default_features_list = [
    RelativePointsCount,
    ContentTagWeight,
    ContentClassWeight,
    ContentIdWeight,
    TotalChildsPerSymbol,
    ChildsPerSymbol,
    RelativeTextLength,
    LinkTextDensity,
    LinkDensity,
    RelativeArea,
    RelativeWidth,
    RelativeHeight,
    InTheMiddleOfWidth,
    InTheMiddleOfHeight,
    ContainsH1,
    TextLengthVsHtmlLength,
    ImgsPerSymbol,
]
