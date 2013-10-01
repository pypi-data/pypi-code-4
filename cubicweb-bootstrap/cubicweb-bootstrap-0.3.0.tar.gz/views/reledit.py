"""bootstrap implementation of reledit

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from logilab.common.decorators import monkeypatch

try:
    from cubes.inlinedit.views import reledit
except:
    reledit = None

if reledit:
    reledit.ReleditRelationFormHandler._addzone = u' <span class="glyphicon glyphicon-plus"></span>'
    reledit.ReleditFormHandler._editzone = u' <span class="glyphicon glyphicon-pencil"></span>'
    reledit.ReleditEntityFormHandler._deletezone = u' <span class="glyphicon glyphicon-remove"></span>'
    reledit.ReleditRelationFormHandler._addzone = u' <span class="glyphicon glyphicon-plus"></span>'
