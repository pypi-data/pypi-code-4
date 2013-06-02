import os, re, smtplib
from email.mime.text import MIMEText
from optparse import OptionParser, OptionGroup

from zope.testbrowser.browser import Browser

#------------------------------------------------------------------------------
def emailMsg(subject, msg, options):
    if not options.smtpTo:
        return

    msg = MIMEText(msg)
    msg['Subject'] = subject
    msg['From'] = options.smtpFrom
    msg['To'] = options.smtpTo

    s = smtplib.SMTP(options.smtpServer, 25)
    if options.smtpLogin:
        s.login(options.smtpLogin, options.smtpPasswd)
    s.sendmail(options.smtpFrom, options.smtpTo, msg.as_string())
    s.quit()

#------------------------------------------------------------------------------
def emailSuccess(options):
    emailMsg("Successfully logged in to account.dyn.com",
             "Successfully logged in to account.dyn.com",
             options)

#------------------------------------------------------------------------------
def emailProblem(browser, options):
    emailMsg("Log in to account.dyn.com failed",
             "Log in to account.dyn.com failed:\n" + browser.contents,
             options)


#------------------------------------------------------------------------------
parser = OptionParser("python -m dynComLogin [options]")

group1 = OptionGroup(parser, "Mandatory 'Options'",
                        "These 'options' must be given.")

group1.add_option("-l", "--login", dest="login",
                    default= os.environ.get("DYN_COM_LOGIN"),
                    help="your dyn.com login. "\
                         "Default: Environment variable DYN_COM_LOGIN")

group1.add_option("-p", "--password", dest="passwd",
                    default= os.environ.get("DYN_COM_PASSWD"),
                    help="your dyn.com password. "\
                         "Default: Environment variable DYN_COM_PASSWD")

parser.add_option_group(group1)

group2 = OptionGroup(parser, "Notification Options",
                        "Specify at least smtpTo if you want to get "\
                        "notification emails.")

group2.add_option("--smtpTo", dest="smtpTo",
                    default=None,
                    help="recipient of email messages. If given then success "\
                         "or failure notifications will be sent to this "
                         "address.")

group2.add_option("--smtpFrom", dest="smtpFrom",
                    default="dynComLogin",
                    help="sender of email messages")

group2.add_option("--smtpServer", dest="smtpServer",
                    default=os.environ.get("SMTP_SERVER", "localhost"),
                    help="SMTP server. Default: "\
                         "Environment variable SMTP_SERVER or 'localhost'")

group2.add_option("--smtpLogin", dest="smtpLogin",
                    default=os.environ.get("SMTP_LOGIN"),
                    help="login for authentification with SMTP server "\
                         "if needed. Default: Environment variable SMTP_LOGIN")

group2.add_option("--smtpPasswd", dest="smtpPasswd",
                    default=os.environ.get("SMTP_PASSWD"),
                    help="password for authentification with SMTP server"\
                         "if needed. Default: Environment variable SMTP_PASSWD")

parser.add_option_group(group2)

(options, args) = parser.parse_args()

if not options.login:
    parser.error("login missing")

if not options.passwd:
    parser.error ("passwd missing")

browser = Browser()
browser.addHeader("User-Agent", "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.5) Gecko/2014121622 Ubuntu/14.10 (ubuntu) Firefox/30.0.5")

browser.open("https://account.dyn.com")

uidControl = browser.getControl(name="username")
uidControl.value = options.login
passwdControl = browser.getControl(name="password")
passwdControl.value = options.passwd
submitControl = browser.getControl(name="submit")
submitControl.click()

if browser.contents.find("Log Out") == -1:
    if options.smtpServer:
        emailProblem(browser, options)
    raise RuntimeError, "Login failed"
else:
    emailSuccess(options)
