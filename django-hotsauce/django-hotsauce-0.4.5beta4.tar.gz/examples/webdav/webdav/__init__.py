from notmm.utils.configparse import setup_all
DAV10_CONFIG = {}
setup_all('DAV', DAV10_CONFIG, c='webdav.conf')
print DAV10_CONFIG
