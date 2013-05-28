import urllib2
import zlib
import urlparse

MIMIC_HEADERS = {
}

def __setup (
    Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    Cookie = '',
    Connection = 'keep-alive',
    Host = 'ele.me',
    User_Agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31",
    Cache_Control = 'max-age=0',
    Accept_Language = 'en-US,en;q=0.8',
    Accept_Encoding = 'gzip,deflate,sdch',
    Accept_Charset = 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',      
    ):
    _map = locals()
    for key in _map:
        MIMIC_HEADERS[key.replace('_', '-')] = _map[key]

def __get_full_html (uri, need_decompress=True):
    return __request_url (uri, need_decompress) [1]

def __request_url (uri, need_decompress=True):
    """
    Get the thml content at a particular url.
    """
    headers = MIMIC_HEADERS
    req = urllib2.Request(uri, None, headers)

    flike = urllib2.urlopen(req)
    cont = flike.read()
    if need_decompress:
        cont = zlib.decompress(cont, 16 + zlib.MAX_WBITS) 

    path = urlparse.urlparse(flike.geturl()).path
    return (path, cont)

def __replace_slash (to_place):
    """
    >>> print (__replace_slash ('a/b'))
    a|b
    """
    return to_place.replace('/', '|')

def __store_html_to_file (html_str, _dir, _name):
    html = html_str
    _rs =  __replace_slash
    file_name = "{}/{}.html".format(_dir, _rs(_name))
    with open(file_name, 'w') as f:
        f.write(html)
    return file_name

store_html_str_to_file =  __store_html_to_file
shtmtofile = store_html_str_to_file
get_html_str_from_url = __get_full_html
r_url = __request_url
setup = __setup

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    setup()
    print (r_url ('http://www.baidu.com')[1])
