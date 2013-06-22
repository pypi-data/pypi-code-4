# -*- coding: utf-8 -*-

from django.conf import settings

#: Enable checking of object level permissions. Note that if this option is
#: enabled, you must plug in an authentication backend that actually does
#: implement object level permissions or no page will be editable.
TREE_EDITOR_OBJECT_PERMISSIONS = getattr(settings,
    'TREE_EDITOR_OBJECT_PERMISSIONS', False)

#: Include ancestors in filtered tree editor lists
TREE_EDITOR_INCLUDE_ANCESTORS = getattr(settings,
    'TREE_EDITOR_INCLUDE_ANCESTORS', False)
