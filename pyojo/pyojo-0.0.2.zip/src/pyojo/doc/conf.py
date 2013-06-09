# -*- coding: utf-8 -*-
#
# pyojo documentation build configuration file, created by
# Txema Vicente <txema@nabla.net>
#

#from docutils.writers.html4css1 import HTMLTranslator
#old_visit_bullet_list = HTMLTranslator.visit_bullet_list


import sys, os
import pprint
_PrettyPrinter = pprint.PrettyPrinter(indent=4)
def pretty(text):
    _PrettyPrinter.pprint(text)
    return _PrettyPrinter.pformat(text)

# patched extensions base path.
sys.path.insert(0, os.path.abspath('.'))
from ext.sphinx_mod import EventDocumenter, find_modules

# pyojo base path.
_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
print "Searching %s" % _path
sys.path.insert(0, _path)
sys.is_epydoc = True
try:
    import pyojo
    import pyojo.js
    import pyojo.js.dojo
    import pyojo.app
    
except:
    print "ERROR: pyojo not found"
    sys.exit(1)

print "Generating pyojo %s Documentation" % (pyojo.__version__)


# Do not try to import these modules
skip_modules = {"pyojo": {
                     "pyojo": ["work"],
                     "pyojo.js.dojo.api": [],
                     "pyojo.tests": None
                     }
               }

f = open('build.log', 'w')
sys.stdout = f

# Skip members
def skip_member(member, obj):
    module = obj.__name__
    fullname = module+"."+member
    print fullname
    if module.startswith("pyojo.base"): return True
    #if module.startswith("pyojo.data"): return True
    #if module.startswith("pyojo.func"): return True
    #if module.startswith("pyojo.debug"): return True
    #if "pyojo.classes" in module: return True
    if member.startswith("X_"): return True
    if fullname=="pyojo.base": return True
    if fullname=="pyojo.route": return True
    if fullname=="pyojo.command": return True
    if fullname=="pyojo.task": return True
    return False

autosummary_generate = True

sys.skip_member = skip_member

for mod in skip_modules.keys():
    sys.all_submodules = find_modules(os.path.join(_path, mod),
                                         skip_modules[mod])


pretty(sys.all_submodules)

extensions = ['sphinx.ext.autodoc',
              'ext.autosummary',
              'sphinx.ext.inheritance_diagram', 
              'sphinx.ext.todo',
              'sphinx.ext.viewcode']

inheritance_graph_attrs = dict(rankdir="LR", size='""') #TB

autodoc_member_order='groupwise'
templates_path = ['ext/templates']
source_suffix = '.txt'
master_doc = 'index'
project = u'pyojo'
copyright = u'2011, Txema Vicente'
version = '0.1'
release = pyojo.__version__
exclude_patterns = ['_build', '_templates']
add_module_names = False
pygments_style = 'sphinx'
modindex_common_prefix = ['pyojo.']
html_theme = 'default'
html_theme_path = ["ext/theme"]
html_title = "pyojo v%s" % (pyojo.__version__)
html_short_title = "pyojo v%s " % (pyojo.__version__)
html_favicon = 'favicon.ico'
html_static_path = ['ext/static']
html_domain_indices = True
html_use_index = True
html_split_index = True
html_show_sourcelink = True
htmlhelp_basename = 'pyojodoc'
latex_elements = {}
latex_documents = [
  ('index', 'pyojo.tex', u'pyojo Documentation',
   u'Txema Vicente', 'manual'),
]
man_pages = [
    ('index', 'pyojo', u'pyojo Documentation',
     [u'Txema Vicente'], 1)
]

texinfo_documents = [
  ('index', 'pyojo', u'pyojo Documentation',
   u'Txema Vicente', 'pyojo', 'One line description of project.',
   'Miscellaneous'),
]

# pyojo documentation --------------------------------------------------


# Generated contents
import time
import datetime

now = datetime.datetime.fromtimestamp(time.time())
with open('build.rst', 'w') as f:
    f.write(".. list-table::\n")
    f.write("   :widths: 50 50\n")
    f.write("\n")
    for var, val in (("Date", now.strftime("%Y/%m/%d %H:%M:%S")),
                     ("pyojo version", pyojo.version)):
        f.write("   * - "+var+"\n     - "+val+"\n")


