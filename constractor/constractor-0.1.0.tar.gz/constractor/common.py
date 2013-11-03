# -*- coding: utf-8 -*-

# Copyright (C) 2013, David Kuryakin (dkuryakin@gmail.com)
#
# This material is provided "as is", with absolutely no warranty expressed
# or implied. Any use is at your own risk.
#
# Permission to use or copy this software for any purpose is hereby granted
# without fee. Permission to modify the code and to distribute modified
# code is also granted without any restrictions.

def elements_are_equal(e1_x, e1_y, e1_width, e1_height, e2_x, e2_y, e2_width, e2_height, max_deviation=0.1):
    if not (e1_width and e1_height and e2_width and e2_height): return False
    if float(abs(e1_width - e2_width)) / min(e1_width, e2_width) > max_deviation: return False
    if float(abs(e1_height - e2_height)) / min(e1_height, e2_height) > max_deviation: return False
    if float(abs(e1_x - e2_x)) / min(e1_width, e2_width) > max_deviation: return False
    if float(abs(e1_y - e2_y)) / min(e1_height, e2_height) > max_deviation: return False
    return True

def train(classes, features):
    from sklearn.ensemble import GradientBoostingClassifier
    learner = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0)
    clf = learner.fit(features, classes)
    result = clf.score(features, classes)
    return result, clf

def page_to_features(page, features_calculator):
    frame = page.mainFrame()
    html = unicode(frame.toHtml())
    text = unicode(frame.toPlainText())
    title = unicode(frame.title())
    doc_geom = frame.geometry()
    meta = dict((unicode(k).lower(), map(unicode, v)) for k, v in frame.metaData().iteritems())

    elements = frame.findAllElements('body *')
    _elements = []
    for element in elements:
        geometry = element.geometry()
        attrs = dict((unicode(an), unicode(element.attribute(an))) for an in element.attributeNames())
        link_texts = map(lambda e: unicode(e.toPlainText()), element.findAll('a'))

        def _childs_count(element):
            childs = 0
            el = element.firstChild()
            last = element.lastChild()
            while True:
                if el.isNull():
                    break
                childs += 1
                if el == last:
                    break
                el = el.nextSibling()
            return childs

        _element = {
            'x': geometry.x(),
            'y': geometry.y(),
            'height': geometry.height(),
            'width': geometry.width(),
            'outer_html': unicode(element.toOuterXml()),
            'inner_html': unicode(element.toInnerXml()),
            'plain_text': unicode(element.toPlainText()),
            'tag': unicode(element.tagName()),
            'classes': map(unicode, element.classes()),
            'attributes': attrs,
            'childs': _childs_count(element),
            'sibling': _childs_count(element.parent()),
            'tot_childs': len(element.findAll('*')),
            'link_texts': link_texts,
            'element': element
        }
        _elements.append(_element)

    doc = {
        'inner_html': html,
        'plain_text': text,
        'title': title,
        'height': doc_geom.height(),
        'width': doc_geom.width(),
        'keywords': meta.get(u'keywords', []),
        'description': meta.get(u'description', [u''])[0]
    }

    result = {
        'elements': _elements,
        'document': doc
    }

    features = []
    for fc in features_calculator:
        fc_obj = fc(result)
        features.append(fc_obj.features())
    features = zip(*features)
    return result, features
