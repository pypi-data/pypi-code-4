
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/mako/MakoCgi - format a Mako Template from text, using CGI variables
{{/include}}

The <code>whiff_middleware/mako/MakoCgi</code>
middleware formats a
<a href="http://www.makotemplates.org/">Mako template [http://www.makotemplates.org/]</a>.
This module will not work unless the Mako template engine is installed separately.
<code>MakoCgi</code> installs any CGI data parameters for the request
as data variables for the Mako template.
The rest of the WHIFF environment is also installed as the special data variable
<CODE>whiff_environment</code>.
This middleware is intended to make it very easy to use Mako
to implement HTML forms and form actions.
<p>
As a security precaution, remotely submitted configurations cannot use this middleware
because Mako templates might facilitate code injection attacks.
{{include "example"}}
{{using targetName}}MakoCgi{{/using}}

{{using page}}

{{include "whiff_middleware/mako/IfMako"}}
{{using page}}
    {{cgi-default species}}Human{{/cgi-default}}

    {{include "whiff_middleware/mako/MakoCgi"}}
    
Greetings ${ species } <br>
Your remote host is ${ whiff_environment.get("REMOTE_HOST", "not specified") } <br>

    {{/include}}
     
{{/using}}

{{using elsePage}}
    MAKO IS NOT INSTALLED!
{{/using}}
{{/include}}

{{/using}}

{{/include}}

Mako is a very fast, powerful, terse, and popular Python text generation
templating engine.  Mako may be superior to WHIFF configuration templates
for formatting complex HTML pages using loops and conditionals.  By using
<code>MakoText</code> an application may use Mako templates to format text
in place of WHIFF configuration templates.
"""

import MakoText
from whiff import resolver
from whiff.middleware import misc
from whiff import whiffenv

class MakoCgi(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        data = {}
        env = resolver.process_cgi(env, parse_cgi=True)
        cgidict = env[whiffenv.CGI_DICTIONARY]
        for (name, value) in cgidict.items():
            if value:
                data[name] = value[0] # just use the first value (caller can use "whiff_environment" if ambiguous)
        data["whiff_environment"] = env.copy()
        application = MakoText.__middleware__(self.page, data)
        return self.deliver_page(application, env, start_response)

__middleware__ = MakoCgi
