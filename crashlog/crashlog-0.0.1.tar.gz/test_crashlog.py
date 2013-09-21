import crashlog
import sys


def test_install():
    emails = ['daffy@looney.org', 'bugs@looney.org']
    logfile = '/path/to/logfile'

    orig_emails = crashlog._EMAILS
    orig_logfile = crashlog._LOGFILE

    try:
        crashlog.install(emails, logfile)
        assert crashlog._EMAILS == emails, 'bad emails'
        assert crashlog._LOGFILE == logfile, 'bad logfile'
        assert sys.excepthook == crashlog.excepthook
    finally:
        crashlog._EMAILS = orig_emails
        crashlog._LOGFILE = orig_logfile
        sys.excepthook = crashlog._PREV_EXCEPTHOOK


