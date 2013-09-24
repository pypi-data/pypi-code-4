from lino.runtime import *
print reception.MyWaitingVisitors.required

ses = settings.SITE.login('hubert')
print ses.user
print ses.user.profile
print repr(ses.user.profile)
print reception.MyWaitingVisitors.get_view_permission(ses.user.profile)


