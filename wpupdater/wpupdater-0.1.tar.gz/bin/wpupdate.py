import argparse
import datetime
import sys
import urllib2
from wpupdater.WPBlog import WPBlog
from wpupdater.SeoChecker import *
from wpupdater.utils import LoginException, WPLoggerAdapter, check_for_new_version

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--username', help='wp-admin login username', required=True)
    ap.add_argument('-p', '--password', help='wp-admin login password', required=True)
    ap.add_argument('-l', '--login-check', dest='login-check', help='Check if credentials are ok', action='store_true', default=False)
    ap.add_argument('-U', '--upgrade', help='Do upgrade blog', action='store_true', default=False)
    ap.add_argument('-r', '--is-upgreadeable', dest='check-if-ready', action='store_true', default=False, help='Check if blog is upgradeable')
    ap.add_argument('url', action='store',help='WordPress address e.g.<www.mywordpress.com>')


    start_time = datetime.datetime.now()
    args = vars( ap.parse_args() )
    blog = WPBlog(args['url'], args['username'], args['password'])
    ret_code = 0
    try:
        blog.login()
        if args['check-if-ready']:
            if blog.check_if_upgradeable():
                print "WordPress site %s is upgradeable!"%args['url']
                ret_code = 0
            else:
                print "WordPress site %s is up-to-date!"%args['url']
                ret_code = 1

        elif args['login-check']:
            """ If no exception returned, credentials are ok """
            print 'Credentials are ok'
            ret_code = 0

        elif args['upgrade']:
            if blog.check_if_upgradeable():
                version = blog.get_current_version()
                print '\t -> \033[92m Current Version = %s, is upgradeable \033[0m'%(version)
                print '\t ->Upgrading....'
                if blog.upgrade():
                    print "\t\t \033[92m -> UPGRADED! \033[0m"
                    ret_code = 0
                else:
                    print "\t\t \033[91m -> UPGRADE ERROR!\033[0m"
                    ret_code = 1

        else:
            print "No args passed, exiting..."
            ret_code = 0

    except LoginException as e:
        print "\t \033[91m -> Login Error! \033[0m"
        ret_code = 1
    except urllib2.URLError:
        print "\t \033[91m -> Error Opening! \033[0m"
        ret_code = 1
    except Exception as e:
        print "UNKNOWN ERROR %s"%e
        ret_code = 1
    stop_time = datetime.datetime.now()
    print "Ended up in %s seconds"%(stop_time - start_time).total_seconds()
    sys.exit(ret_code)

if __name__ == "__main__":
    main()
