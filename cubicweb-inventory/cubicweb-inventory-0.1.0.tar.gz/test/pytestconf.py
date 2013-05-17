import os
import pwd


def getlogin():
    """avoid using os.getlogin() because of strange tty / stdin problems
    (man 3 getlogin)
    Another solution would be to use $LOGNAME, $USER or $USERNAME
    """
    return pwd.getpwuid(os.getuid())[0]


def update_parser(parser):
    login = getlogin()
    parser.add_option('-u', '--dbuser', dest='dbuser', action='store',
                      default=login, help="database user")
    parser.add_option('-w', '--dbpassword', dest='dbpassword', action='store',
                      default=login, help="database password")
    parser.add_option('-n', '--dbname', dest='dbname', action='store',
                      default=None, help="database name")
    parser.add_option('--euser', dest='euser', action='store',
                      default=login, help="esuer name")
    parser.add_option('--epassword', dest='epassword', action='store',
                      default=login, help="euser's password' name")
    return parser
