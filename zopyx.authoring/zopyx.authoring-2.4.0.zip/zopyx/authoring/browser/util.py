#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os
import shutil
import lxml.html

def safe_invokeFactory(folder, portal_type, id, **kw):

    candidates = [id]
    for i in range(2, 50):
        candidates.append('%s-%d' % (id, i))

    for c in candidates:
        if c in folder.objectIds():
            continue

        folder.invokeFactory(portal_type, c, **kw)
        return c

    raise RuntimeError('Unable to create %s with a unique ID (%s)' % (portal_type, folder.absolute_url(1)))

def extract_table(html, id):
    root = lxml.html.fromstring(html)
    nodes = root.xpath('//table[@id="%s"]' % id)
    if len(nodes) == 1:
        return lxml.html.tostring(nodes[0])
    return ''

def preflight(workdir):
    """ Check the export HTML file and resources for consistency """

    errors = list()

    root = lxml.html.fromstring(file(os.path.join(workdir, 'index.html')).read())

    # check all stlyes references
    for link in root.xpath('//link'):
        href = link.get('href')
        if not os.path.exists(os.path.join(workdir, href)):
            errors.append('Stylesheet "%s" does not exist' % href)

    # check all image references
    for img in root.xpath('//img'):
        src = img.get('src')
        if not os.path.exists(os.path.join(workdir, src)):
            errors.append('Image "%s" does not exist' % src)

    return errors

def safe_unlink(file_or_directory):
    """ Safe removal of a file or directory """
    if not os.path.exists(file_or_directory):
        return
    if os.path.isfile(file_or_directory):
        os.unlink(file_or_directory)
    else:
        shutil.rmtree(file_or_directory)

