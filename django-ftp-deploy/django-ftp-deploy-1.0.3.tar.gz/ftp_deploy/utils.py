from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail

def ftp_makedirs(ftp, ftp_path, dirname):
    """
    Create directories over FTP
    """
    dirname = dirname.split("/")
    for i in xrange(len(dirname)):
        current = "/".join(dirname[:i + 1]).encode('ascii', 'ignore')
        try:
            ftp.dir(ftp_path + current)
        except:
            ftp.mkd(ftp_path + current)


