import time

from twisted.trial.reporter import VerboseTextReporter
import objc


__version__ = "0.1.2"


NSUserNotification = objc.lookUpClass("NSUserNotification")
NSUserNotificationCenter = objc.lookUpClass("NSUserNotificationCenter")

if not NSUserNotification or not NSUserNotificationCenter:
    raise ImportError(
        "NSUserNotifcation is not supported by your version of Mac OS X"
    )


class OSXNotifierReporter(VerboseTextReporter):
    def addError(self, test, error):
        super(OSXNotifierReporter, self).addError(test, error)
        _, exception, _ = error
        notify("Error: {0}".format(test.id()), exception)

    def addFailure(self, test, failure):
        super(OSXNotifierReporter, self).addFailure(test, failure)
        _, exception, _ = failure
        notify("Test failed: {0}".format(test.id()), exception)

    def done(self):
        super(OSXNotifierReporter, self).done()
        outcome = "Success" if self.wasSuccessful() else "Failed"
        summary = "{0} tests, {1} failures, {2} errors".format(
            self.testsRun, len(self.failures), len(self.errors),
        )
        notify("Trial Run Complete: " + outcome, summary)


def notify(title, subtitle=None):
    notification = NSUserNotification.alloc().init()
    notification.setTitle_(str(title))
    if subtitle:
        notification.setSubtitle_(str(subtitle))

    notification_center = NSUserNotificationCenter.defaultUserNotificationCenter()
    notification_center.deliverNotification_(notification)
