#!/usr/bin/env python

class dsn(object):
    '''
    This class checks, normalizes and store passwords for Data Source Names.
    '''

    def __init__(self, url, dry_run=False, *args, **kwargs):
        '''
        Arguments
        ---------
        url     -- a database connection string, for example:
                       "postgres://username:password@localhost/sample"
                   Note: when the username is not informed, it is retrieved
                         from the environment variable ${USER}
        dry_run -- if True, avoids storing passwords into the standard backing
                   store defined for a given protocol. For example, in the case
                   of Postgres databases, passords are stored in ~/.pgpass
                   ( default: False)
        '''
        super(dsn, self).__init__(*args, **kwargs)
        self.url = url
        self.dry_run = dry_run

    def _invalid(self, what, msg):
        raise RuntimeError('invalid %s: %s' % (what, msg))

    def _simple_database(self, path):
        import re
        d = re.match('^/(\w+)$', path)
        if d is None: self._invalid('database', path)
        return d.group(1)

    def _prompt(self, realm=None, confirm=True):
        import getpass
        ptext = 'Password: ' if realm is None else '[' + realm + '] Password: '
        ctext = 'Confirm: '  if realm is None else '[' + realm + '] Confirm: '
        password = getpass.getpass(ptext)
        confirm  = getpass.getpass(ctext) if confirm else None
        return (password, confirm)

    def _pgsql_check(self, url, protocol, username, hostname, port, database, options):
        if options is not None and len(options) > 0: self._invalid('database', url)

    def _pgsql_passwd(self, hostname, port, database, username, url=None):
        '''
        Allows a password to be defined for a given tuple
        (hostname, port, database, username)

        '''
        import os

        def touch(self, path, mode='a+'):
            fd = os.open(path, os.O_RDWR|os.O_CREAT, 00700)
            return os.fdopen(fd, mode)

        pgpass = os.path.expanduser('~/.pgpass')
        if os.path.exists(pgpass):
            with open(pgpass, 'r') as f:
                for line in f:
                    (h, p, d, u, password) = line.strip().split(':')
                    if not( h == '*' or h  == hostname ): continue
                    if not( p == '*' or int(p) == port ): continue
                    if not( d == '*' or d  == database ): continue
                    if not( u == '*' or u  == username ): continue
                    return password
        # at this point, a password prompt is presented to the user
        ( password, confirm ) = self._prompt(url)
        # if passwords match, write it down to ~/.pgpass
        if password == confirm:
            if not self.dry_run:
                with self.touch(pgpass) as f:
                    f.write('%s:%d:%s:%s:%s' % (hostname, port, database, username, password))
            return password
        else:
            raise RuntimeError('Passwords mismatch')
        
    _ports  = { 'postgresql': 5432, }
    _check  = { 'postgresql': _pgsql_check, }
    _passwd = { 'postgresql': _pgsql_passwd, }

    def check(self):
        '''
        Parses a database url and returns its components.
        Perform protocol specific validations and eventually allows the
        password for the given username to be defined, if allowed by the
        given protocol.

        Arguments
        ---------
        none

        Returns
        -------
        a dictionary containing with components

        Example
        -------
        >>> url = 'postgresql://rgomes:secret@localhost/sample'
        >>> import distcontrib_migrate
        >>> m = distcontrib_migrate.dsn(url).check()
        >>> m['protocol']
        'postgresql'
        >>> m['username']
        'rgomes'
        >>> m['hostname']
        'localhost'
        >>> m['port']
        5432
        >>> m['database']
        'sample'
        >>> m['options']
        []
        >>> m['password']
        'secret'
        
        '''
        import os
        from urlparse import urlparse

        url = self.url
        u = urlparse(url)
        if u is None: self._invalid('url', url)
        # check protocol, username, hostname and database path
        if u.scheme   is None or len(u.scheme)        < 1: self._invalid('protocol', url)
        if u.hostname is None or len(u.hostname)      < 1: self._invalid('hostname', url)
        if u.path     is None or len(u.path)          < 2: self._invalid('database', url)
        if u.params   is not None and len(u.params)   > 0: self._invalid('params (must be empty)', url)
        if u.query    is not None and len(u.query)    > 0: self._invalid('query (must be empty)', url)
        if u.fragment is not None and len(u.fragment) > 0: self._invalid('fragment (must be empty)', url)
        # check username
        if u.username is None or len(u.username) < 1:
            username = os.environ['LOGNAME']
        else:
            username = u.username
        # check port number
        if u.port is not None:
            port = u.port
        else:
            port = self._ports[u.scheme]
        # find database-specific parameters, if any
        p = u.path.split(';')
        database = self._simple_database(p[0])
        options  = p[1:]
        # perform database-specific checkings
        check = self._check[u.scheme]
        if check is None: self._invalid('protocol (not implemented yet)', url)
        check(self, url, u.scheme, username, u.hostname, port, database, options)
        # retrieve password, if necessary
        if u.password is None or len(u.password) < 1:
            passwd = self._passwd[u.scheme]
            if passwd is None: self._invalid('protocol (not implemented yet)', url)
            password = passwd(self, u.hostname, port, database, username, url=url)
        else:
            password = u.password
        # return url components
        d = {}
        d['protocol'] = u.scheme
        d['username'] = username
        d['password'] = password
        d['hostname'] = u.hostname
        d['port']     = port
        d['database'] = database
        d['options']  = options
        return d

    def normalize(self):
        '''
        Parses a database url and returns a canonical format of it.
        Perform protocol specific validations and eventually allows the
        initial password to be set, if allowed for the given protocol.
        Notice that the password is never returned to the caller.

        Arguments
        ---------
        none

        Returns
        -------
        a normalized URL connection string

        Example
        -------
        >>> url = 'postgresql://localhost/sample'
        >>> import distcontrib_migrate
        >>> distcontrib_migrate.dsn(url).normalize()
        'postgresql://rgomes@localhost:5432/sample'
        >>> url = 'postgresql://rgomes:secret@localhost/sample'
        >>> distcontrib_migrate.dsn(url).normalize()
        'postgresql://rgomes@localhost:5432/sample'
        
        '''
        u = self.check()
        opts = u['options']
        if opts is None or len(opts) == 0:
            options = ''
        else:
            options = ';'.join(opts)
        return ''.join([
            u['protocol'],
            '://',
            u['username'],
            '',                   #-- ':' + u['password'] if u['password'] else '',
            '@',
            u['hostname'],
            ':',
            str(u['port']),
            '/',
            u['database']
        ]) + options
