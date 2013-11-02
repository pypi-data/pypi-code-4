# -*- coding: utf-8 -*-
'''
daemon module emulating BSD Daemon(3)

Copyright 2013 Yoshida Shin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os
import errno


__all__ = ['daemon']


def daemon(nochdir=False, noclose=False):
    r''' Fork twice and become a daemon.

         If argument `nochdir' is False, this process changes the calling
         process's current working directory to the root directory ("/");
         otherwise, the current working directory is left unchanged.
         The Default of nochdir is False.

         If  argument `noclose' is False,
         this function close file descriptor 0, 1 and 2 and reopen /dev/null;
         otherwise, leave them.
         The defult value of noclose is False.

         daemon returns the pid of new process.
    '''

    ## 1st fork
    pid = os.fork()
    if pid != 0:
        os.waitpid(pid, os.P_WAIT)
        os._exit(0)

    ## 2nd fork
    os.setsid()
    if os.fork() != 0:
        os._exit(0)

    ## daemon process
    # ch '/'
    if not nochdir:
        os.chdir('/')

    if not noclose:
        # close stdin, stdout, stderr
        for i in xrange(3):
            try:
                os.close(i)
            except OSError as e:
                # Do nothing if the descriptor has already closed.
                if e.errno == errno.EBADF:
                    pass

        # Open /dev/null for stdin, stdout, stderr
        os.open(os.devnull, os.O_RDONLY)  # stdin
        os.open(os.devnull, os.O_WRONLY)  # stdout
        os.dup(1)                         # stderr

    return os.getpid()
