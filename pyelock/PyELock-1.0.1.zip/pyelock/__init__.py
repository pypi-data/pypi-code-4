import socket
import re

class ELockException(Exception): pass

class BadRequest(ELockException): pass
class BadResponse(ELockException): pass
class LockInUse(ELockException): pass
class Timeout(ELockException): pass
class ConnectionClosed(ELockException): pass

class ELock(object):
    """Communicates with an elock server to perform operations on locks."""

    def __init__(self, remote_endpoint):
        '''
        Initializes an elock session.
        @param remote_endpoint elock server endpoint, e.g. ('127.0.0.1', 11400).
        @raise socket.error: If a communications error with the server occurs.
        @raise ELockException: If the server returns a bad response.
        '''
        self.socket = socket.socket()
        self.socket.connect(remote_endpoint)

        # This class doesn't support resuming connections, so set
        # the abandon timeout to zero.
        code,message = self.__cmd("set_timeout 0")
        if code != 200:
            raise BadResponse()

    def close(self):
        '''
        Closes the connection to the elock server.
        Note that this will immediately release all held locks.
        @raise socket.error: If a communications error with the server occurs.
        '''
        if self.socket:
            self.socket.close()
            self.socket = None

    def lock(self, name, timeout=None):
        '''
        Acquire a lock.
        @name Name of the lock (cannot contain spaces).
        @timeout Time to wait for the lock if it's in use, in seconds.
            If None (the default), return immediately if the lock is in use.
        @return True if the lock was acquired; False otherwise.
        @raise socket.error: If a communications error with the server occurs.
        @raise ELockException: If the server returns a bad response.
        @note If you already hold a lock, locking it again will succeed.  However,
            multiple holds will not stack, such that a single unlock() will release
            the lock entirely, even after a number of lock() calls.
        '''

        cmd = 'lock %s%s' % (name, ' ' + str(timeout) if timeout else '')
        code, response = self.__cmd(cmd, timeout=(timeout or 0) + 10.0)
        if code == 200:
            return True
        elif code == 409:
            return False
        else:
            raise BadResponse()

    def unlock(self, name):
        '''
        Release an acquired lock.
        @name Name of the lock (cannot contain spaces).
        @return True if the lock was released; False if you did not own the lock.
        @raise socket.error: If a communications error with the server occurs.
        @raise ELockException: If the server returns a bad response.
        '''
        code, response = self.__cmd('unlock ' + name)
        if code == 200:
            return True
        elif code == 403:
            return False
        else:
            raise BadResponse()

    def unlock_all(self):
        '''
        Releases all locks held by the current session.
        @return True
        @raise socket.error: If a communications error with the server occurs.
        @raise ELockException: If the server returns a bad response.
        '''
        code, response = self.__cmd('unlock_all')
        if code != 200:
            raise BadResponse()
        return True

    def __cmd(self, command, timeout=10.0):
        if not self.socket:
            raise ConnectionClosed()

        self.socket.settimeout(timeout)
        self.socket.sendall(command + "\r\n")
        buffer = ""
        while '\r\n' not in buffer:
            try:
                buffer += self.socket.recv(1024)
            except socket.timeout as e:
                raise Timeout()

        try:
            code, message = self.__read_status(buffer)
        except:
            raise BadResponse()

        if code == 400:
            raise BadRequest()

        return code,message

    def __read_status(self, line):
        status, msg = line.strip().split(' ', 1)
        return int(status), msg

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

class ELockSingle(object):
    def __init__(self, remote_endpoint, lock_name, timeout=None):
        self.elock = ELock(remote_endpoint)
        if not self.elock.lock(lock_name, timeout):
            raise LockInUse()

    def __del__(self):
        self.elock.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.elock.close()
