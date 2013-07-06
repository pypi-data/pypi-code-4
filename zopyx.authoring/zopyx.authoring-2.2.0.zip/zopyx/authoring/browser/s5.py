#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

""" Convert HTML to S5 """

import os
import lxml.html
from zopyx.smartprintng.plone import xpath_query


def _cleanupHtml(html):
    return lxml.html.tostring(lxml.html.fromstring(html.strip()), encoding=unicode)

def splitHTMLIntoSlides(source_html):

    root = lxml.html.fromstring(source_html)
    body = root.xpath('//div[@id="main-content"]')[0]

    # h1 tags are obsolete in S5 since we promote all H2 tags to H1 tags below
    for heading in body.xpath('//h1'):
        heading.getparent().remove(heading)

    # Each slide in S5 starts with a H1 tag. Each slide in HTML (aggregated or not)
    # is represented by a H2 tag and the markup until the next H2 tag. So we
    # need to shift all H2 tags to H1 etc.  In addition we need to split the
    # HTML documents at H1 tags (formerlly H2 tags).

    # h2->h1, h3->h2, ...
    for heading in body.xpath(xpath_query(('h2', 'h3', 'h4', 'h5'))):
        heading.text = heading.text_content()
        level = int(heading.tag[1:])
        heading.tag= 'h%d' % (level - 1)

    # now split the page into chunks at each H1 tag which is the marker for a
    # new slide
    current_doc = list()
    slides = list()
    html2 = lxml.html.tostring(body, encoding=unicode)
    for line in html2.split('\n'):
        line = line.rstrip()
        if '<h1' in line.lower() and current_doc:
            html = u' '.join(current_doc)
            # add only slides if they have a h1 tag in it (ignoring
            # trailing HTML junk)
            if '<h1' in html:
                slides.append(_cleanupHtml(html))
            current_doc = [line]
        else:
            current_doc.append(line)

    html = u' '.join(current_doc)
    slides.append(_cleanupHtml(html))
    return slides

def html2s5(context, html_filename):

    html = file(html_filename).read()
    slides = splitHTMLIntoSlides(html)

    # retrieve presentation helper view
    s5view = context.restrictedTraverse('@@s5_presentation_template')

    # get hold of metadata for rendering the S5 view 
    content_folder = context.getContentFolder()
    conversion_folder = context.getConversionFolder()

    # parameter dict
    params = dict(s5line1=conversion_folder.getS5Line1(),
                  s5line2=conversion_folder.getS5Line2(),
                  s5line3=conversion_folder.getS5Line3(),
                  s5line4=conversion_folder.getS5Line4()
                  )
    for field in content_folder.Schema().fields():
        params[field.getName()] = field.get(content_folder)

    # now render s5
    html = s5view(slides=slides, **params)

    s5_filename = os.path.join(os.path.dirname(html_filename), 'index_s5.html')
    file(s5_filename, 'wb').write(html.encode('utf-8'))
    return s5_filename
