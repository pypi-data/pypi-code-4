import logging
import logging.handlers
import socket
import sys
import traceback

# This is a guess at a long enough string based on
# https://bugzilla.mozilla.org/show_bug.cgi?id=901754#c1
MAX_SIZE = 60000

# Hopefully this will go to sentry.
log = logging.getLogger('logging')


class UnicodeHandler(logging.handlers.SysLogHandler):

    # Not sure if we need to do this, but that celery monkey patches
    # logs without this seems scary.
    _signal_safe = True

    def emit(self, record):
        if hasattr(self, '_fmt') and not isinstance(self._fmt, unicode):
            # Ensure that the formatter does not coerce to str. bug 734422.
            self._fmt = unicode(self._fmt)

        try:
            msg = self.format(record)[:MAX_SIZE] + '\000'
        except UnicodeDecodeError:
            # At the very least, an error in logging should never propogate
            # up to the site and give errors for our users. This should still
            # be fixed.
            msg = u'A unicode error occured in logging \000'

        prio = '<%d>' % self.encodePriority(self.facility,
                                            self.mapPriority(record.levelname))
        if type(msg) is unicode:
            msg = msg.encode('utf-8')
        msg = prio + msg
        try:
            print msg
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except socket.error:
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            else:
                self.socket.sendto(msg, self.address)

            self.emitted(self.__class__.__name__.lower())
        except (KeyboardInterrupt, SystemExit):
            raise
        except socket.error, value:
            self.handleError(record, value.strerror)
        except:
            self.handleError(record, 'UnicodeHandler error')

    def handleError(self, record, message):
        sys.stderr.write(message)
        traceback.print_exc()
        log.exception(message)

    def emitted(self, name):
        """Hook for tests to patch."""
        pass
