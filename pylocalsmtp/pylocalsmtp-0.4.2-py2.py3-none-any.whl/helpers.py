from peewee import SqliteDatabase
from .settings import *


DB = SqliteDatabase(DB_NAME)

WELCOME_MAIL_BODY = """Hi and thank you for installing PyLocalSmtp,

You are currently running the web interface and you'll see your incoming mail right here.
By default, the smtp server runs under 127.0.0.1:1025, so configure your local application with those params.

 * If you want to customize things, take a look at the command line : 'pylocalsmtpd --help'
 * You can find the source code here : https://bitbucket.org/m_clement/pylocalsmtp/
 * Please report any issue here : https://bitbucket.org/m_clement/pylocalsmtp/issues

Have fun !
- Martyn"""
