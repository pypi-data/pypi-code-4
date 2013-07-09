
from whiff.middleware import misc
from whiff import resolver
from whiff import whiffenv

class fieldSetup(misc.utility):
    def __call__(self, env, start_response):
        env = resolver.process_cgi(env, parse_cgi=True)
        cgiDict = env[whiffenv.CGI_DICTIONARY]
        L = []
        for name in cgiDict:
            if not name.startswith('_'):
                value = whiffenv.cgiGet(env, name)
                L.append('addField("%s", "%s");\n' % (name, value))
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        return L

__middleware__ = fieldSetup
