# Zope2 stuff
EditorRate = "Content Ratings: Editor Rate"
ViewEditorialRating = "Content Ratings: View Editorial Rating"
UserRate = "Content Ratings: User Rate"
ViewUserRating = "Content Ratings: View User Rating"

try:
    # Set some default roles for zope2
    from AccessControl.Permission import addPermission
except ImportError:
    pass
else:
    addPermission(EditorRate, default_roles=('Manager', 'Reviewer'))
    addPermission(ViewEditorialRating, default_roles=('Anonymous', 'Authenticated',))
    addPermission(UserRate, default_roles=('Anonymous', 'Authenticated',))
    addPermission(ViewUserRating, default_roles=('Anonymous','Authenticated',))


