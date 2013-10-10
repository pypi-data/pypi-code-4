#! /usr/bin/env python

VERSION =   "1.0.1"

import os, sys, ConfigParser, time, urllib
from xml.dom import minidom

DEFAULT_COLOR   =   "\033[0;0m"
ERROR_COLOR     =   "\033[31m"
ALERT_COLOR     =   "\033[33m"
OK_COLOR        =   "\033[92m"

def alert(text, error_code = None, color = None, piped = False):
    if not piped and not sys.stdout.isatty():
        return
    if piped and not sys.stdout.isatty():
        if error_code is not None:
            sys.stderr.write("%s\n" % text)
            sys.stderr.flush()
            sys.exit(error_code)
        else:
            sys.stdout.write("%s\n" % text)
            sys.stdout.flush()
    else:
        if error_code is not None:
            sys.stderr.write("%s%s%s\n\n" % (color or (OK_COLOR if error_code == os.EX_OK else ERROR_COLOR), text, DEFAULT_COLOR))
            sys.stderr.flush()
            sys.exit(error_code)
        else:
            sys.stdout.write("%s%s%s\n\n" % (color or DEFAULT_COLOR, text, DEFAULT_COLOR))
            sys.stdout.flush()

# check for updates
PYPI_URL        =   "https://pypi.python.org/pypi?:action=doap&name=s3domain"
CHECK_FILE      =   os.path.expanduser("~/.s3domain-update-check")
if not os.path.exists(CHECK_FILE):
    try:
        open(CHECK_FILE, "w")
    except IOError:
        pass
try:
    last_checked    =   int(open(CHECK_FILE, "r").read().strip())
except ValueError:
    last_checked    =   0
now =   int(time.time())
if now - last_checked > 86400:
    # it has been a day since the last update check
    try:
        pypi_data       =    minidom.parse(urllib.urlopen(PYPI_URL))
        pypi_version    =    pypi_data.getElementsByTagName("revision")[0].firstChild.data
        if pypi_version > VERSION:
            alert("There has been an update for s3domain. Version %s is now available.\nPlease see http://dryan.github.io/s3domain or run `pip install --upgrade s3domain`." % pypi_version, color = ALERT_COLOR)
    except:
        pass
    check_file  =   open(CHECK_FILE, "w")
    check_file.write(str(now))
    check_file.flush()
    check_file.close()

try:
    import boto
except ImportError:
    alert("Please install boto. `pip install boto`", os.EX_UNAVAILABLE)

from boto.s3.website import WebsiteConfiguration, RedirectLocation, RoutingRules

try:
    import argparse
except ImportError:
    alert("Please install argparse. `pip install argparse`", os.EX_UNAVAILABLE)

try:
    from urlparse import urlparse
except ImportError:
    alert("Please install urlparse. `pip install urlparse`", os.EX_UNAVAILABLE)

if "-v" in sys.argv or "--version" in sys.argv:
    # do this here before any of the config checks are run
    alert("s3domain %s" % VERSION, os.EX_OK, DEFAULT_COLOR)

parser          =   argparse.ArgumentParser()
parser.add_argument("bucket_name", help = "The name of the bucket to create", type = str)
parser.add_argument("-l", "--location", help = "The region to create the bucket in", choices = ["USA", "EU"], default = "USA")
parser.add_argument("-a", "--access-key", help = "AWS Access Key ID", type = str)
parser.add_argument("-s", "--access-secret", help = "AWS Access Key Secret", type = str)
parser.add_argument("-w", "--www", help = "Make a second bucket with www. prepended to bucket_name (defaults to false). Web requests are either redirected to bucket_name or the location passed with --redirect.", action = "store_true", default = False)
parser.add_argument("-d", "--dns", help = "Set up the DNS records on Route53 (defaults to false)", action = "store_true", default = False)
parser.add_argument("--dns-zone", help = "The DNS zone name to use for Route53 records (defaults to bucket_name).")
parser.add_argument("-i", "--index", help = "The name to use for Index Documents (defaults to index.html)", type = str, default = "index.html")
parser.add_argument("-e", "--error", help = "The name to use for Error Documents (defaults to 404.html)", type = str, default = "404.html")
parser.add_argument("-r", "--redirect", help = "URI or domain to redirect all requests to", type = str)

args            =   parser.parse_args()

AWS_KEY         =   args.access_key
AWS_SECRET      =   args.access_secret

# look for credentials file in this directory
if os.path.exists(".aws"):
    local_config    =   ConfigParser.ConfigParser()
    local_config.read(".aws")
    if local_config.has_section("Credentials"):
        if AWS_KEY is None:
            AWS_KEY     =   local_config.get("Credentials", "aws_access_key_id")
        if AWS_SECRET is None:
            AWS_SECRET  =   local_config.get("Credentials", "aws_secret_access_key")

# lookup global AWS keys if needed
if AWS_KEY is None:
    AWS_KEY     =   boto.config.get("Credentials", "aws_access_key_id")
    
if AWS_SECRET is None:
    AWS_SECRET  =   boto.config.get("Credentials", "aws_secret_access_key")
    
# lookup AWS key environment variables
if AWS_KEY is None:
    AWS_KEY     =   os.environ.get("AWS_ACCESS_KEY_ID")
if AWS_SECRET is None:
    AWS_SECRET  =   os.environ.get("AWS_SECRET_ACCESS_KEY")

ENDPOINT_IDS    =   {
    "s3-website-us-east-1.amazonaws.com": "Z3AQBSTGFYJSTF",
    "s3-website-us-west-2.amazonaws.com": "Z3BJ6K6RIION7M",
    "s3-website-us-west-1.amazonaws.com": "Z2F56UZL2M1ACD",
    "s3-website-eu-west-1.amazonaws.com": "Z1BKCTXD74EZPE",
    "s3-website-ap-southeast-1.amazonaws.com": "Z3O0J2DXBE1FTB",
    "s3-website-ap-southeast-2.amazonaws.com": "Z1WCIGYICN2BYD",
    "s3-website-ap-northeast-1.amazonaws.com": "Z2M4EHUR26P7ZW",
    "s3-website-sa-east-1.amazonaws.com": "Z7KQH4QJS55SO",
    "s3-website-us-gov-west-1.amazonaws.com": "Z31GFT0UA1I2HV",    
}

def create_bucket(name, redirect):
    s3          =   boto.connect_s3(AWS_KEY, AWS_SECRET)
    bucket      =   s3.create_bucket(name)
    if redirect:
        uri         =   urlparse(redirect)
        redirect    =   RedirectLocation(uri.netloc if uri.netloc else uri.path, uri.scheme if uri.scheme and uri.scheme in ["http", "https"] else "http")
        bucket.configure_website(redirect_all_requests_to = redirect)
    else:
        bucket.configure_website(args.index, args.error)
    return bucket

def set_dns(zone, record, endpoint):
    route53     =   boto.connect_route53(AWS_KEY, AWS_SECRET)
    hosted_zone =   None
    for z in route53.get_zones():
        if z.name == zone:
            hosted_zone     =   z
    if not hosted_zone:
        hosted_zone =   route53.create_zone(zone)
    changes =   route53.get_all_rrsets(hosted_zone.id)
    change  =   None
    for c in changes:
        if c.name.rstrip(".") == record and c.type == "A" and c.alias_dns_name.rstrip(".") == endpoint and c.alias_hosted_zone_id == ENDPOINT_IDS[endpoint]:
            change  =   c
    if not change:
        change  =   changes.add_change("CREATE", record, "A", alias_hosted_zone_id = ENDPOINT_IDS[endpoint], alias_dns_name = endpoint)
        change.add_value("ALIAS %s (%s)" % (endpoint, ENDPOINT_IDS[endpoint]))
        changes.commit()
    return hosted_zone

def main():
    root_bucket     =   create_bucket(args.bucket_name, args.redirect)
    if args.redirect:
        alert("%s created and redirecting to %s" % (root_bucket.name, args.redirect), color = OK_COLOR)
    else:
        alert("%s created at %s" % (root_bucket.name, root_bucket.get_website_endpoint()), color = OK_COLOR)
    www_bucket      =   None
    if args.www:
        www_bucket  =   create_bucket(".".join(["www", args.bucket_name.lstrip(".")]), args.redirect if args.redirect else args.bucket_name)
        alert("%s created and redirecting to %s" % (www_bucket.name, args.redirect if args.redirect else args.bucket_name), color = OK_COLOR)
    if args.dns:
        zone        =   args.dns_zone or args.bucket_name.rstrip(".") + "."
        root_zone   =   set_dns(zone, root_bucket.name, root_bucket.get_website_endpoint().replace(zone, ""))
        if sys.stdout.isatty():
            alert("DNS zone setup for %s" % zone.rstrip("."), color = OK_COLOR)
            alert("Nameservers:", color = ALERT_COLOR)
            alert("%s" % "\n".join([x.rstrip('.') for x in root_zone.get_nameservers()]), color = ALERT_COLOR, piped = True)
            alert("DNS record created for %s" % root_bucket.name, color = OK_COLOR)
        else:
            alert("%s %s" % (zone.rstrip("."), " ".join([x.rstrip(".") for x in root_zone.get_nameservers()])), piped = True)
        if www_bucket:
            www_zone    =   www_bucket.name.rstrip(".") + "."
            www_zone    =   set_dns(zone, www_bucket.name, www_bucket.get_website_endpoint().replace(www_zone, ""))
            alert("DNS record created for %s" % www_bucket.name, color = OK_COLOR)
    sys.exit(os.EX_OK)

if __name__ == "__main__":
    main()

