from twisted.plugin import IPlugin
from twisted.trial.itrial import IReporter
from zope.interface import implementer


@implementer(IPlugin, IReporter)
class OSXNotifier(object):
    description = "OS X Mountain Lion Notifier"
    longOpt = "notify"

    module = "trialosxnotifier"
    klass = "OSXNotifierReporter"


notifier = OSXNotifier()
