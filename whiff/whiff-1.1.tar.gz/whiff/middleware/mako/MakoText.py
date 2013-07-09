
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/mako/MakoText - format a Mako Template from text
{{/include}}

The <code>whiff_middleware/mako/MakoText</code>
middleware formats a
<a href="http://www.makotemplates.org/">Mako template [http://www.makotemplates.org/]</a>.
This module will not work unless the Mako template engine is installed separately.
<p>
As a security precaution, remotely submitted configurations cannot use this middleware
because Mako templates might facilitate code injection attacks.

{{include "example"}}
{{using targetName}}MakoText{{/using}}
{{using page}}

{{include "whiff_middleware/mako/IfMako"}}
{{using page}}

    {{include "whiff_middleware/mako/MakoText"}}
        {{using data}}
	    { "rows":
	            [ ["Pigs", 10],
        	      ["Dogs", 15],
              	      ["Bunnies", 3],
              	      ["Cats", -400]
	              ]
		}
        {{/using}}
        {{using page}}
        
        <table border>
        % for row in rows:
            ${makerow(row)}
        % endfor
        </table>
            
        <%def name="makerow(row)">
            <tr>
            % for name in row:
                <td>${name}</td>
            % endfor
            </tr>
        </%def>
            
        {{/using}}
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

from whiff.middleware import misc
from whiff import whiffenv
import types

class MakoText(misc.utility):
    def __init__(self,
                 page,
                 data=None
                 ):
        self.page = page
        self.data = data
    def __call__(self, env, start_response):
        try:
            from mako.template import Template
        except ImportError:
            raise ImportError, "you must install the mako package from http://www.makotemplates.org/ before using the MakoText middleware"
        # since Mako evaluates python code, disallow rpc tainted environments
        assert not whiffenv.rpc_tainted(env), "security violation: can't evaluate Mako template from tainted environment"
        makoTemplateText = self.param_value(self.page, env)
        makoTemplateData = self.param_json(self.data, env)
        if makoTemplateData is None:
            makoTemplateData = {}
        assert type(makoTemplateData) is types.DictType, "Mako template data must be a mapping of names to values"
        # convert unicode names to byte strings...
        D = {}
        for (name, value) in makoTemplateData.items():
            D[str(name)] = value
        # xxxx could add additional data validations here...
        mytemplate = Template(makoTemplateText)
        result = mytemplate.render(**D)
        return self.deliver_page(result, env, start_response)

__middleware__ = MakoText
