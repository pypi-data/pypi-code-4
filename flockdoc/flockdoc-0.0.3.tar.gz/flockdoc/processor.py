import os

from .content.code import CodePage
from .content.markdown import MarkdownPage
from .content.static import StaticPage

def tree_files(root):
    'get files in a tree for the root'
    for root, dirs, files in os.walk(root):
        for filename in files:
            yield os.path.join(root, filename)

def render_all(source, destination):
    'render all the files in the tree'
    for filename in tree_files(source):
        render_single(filename, source, destination)

def render_single(filename, source, destination):
    'render a single file out to a given destination'
    # determine class
    cls = None

    if filename.endswith('.md'):
        cls = MarkdownPage
    elif 'code' in filename:
        cls = CodePage
    else:
        cls = StaticPage

    filename, content = cls(filename, open(filename, 'r').read()).render()

    print 'Generating %s...' % filename.replace(source, '{%s => %s}' % (source, destination)),

    new = filename.replace(source, destination)
    try:
        os.makedirs(os.path.dirname(new))
    except OSError:  # already exists
        pass

    with open(new, 'w') as f:
        f.write(content)
        print "done"
