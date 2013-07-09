
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/mako/MakoFile - format a Mako Template from file
{{/include}}

The <code>whiff_middleware/mako/MakoText</code>
middleware formats a
<a href="http://www.makotemplates.org/">Mako template [http://www.makotemplates.org/]</a>
where the template is given as the contents of an external file.
This module will not work unless the Mako template engine is installed separately.
<p>
As a security precaution, remotely submitted configurations cannot use this middleware
because Mako templates might facilitate code injection attacks.

{{include "example"}}
{{using targetName}}MakoFile{{/using}}
{{using page}}

{{include "whiff_middleware/mako/IfMako"}}
{{using page}}

    {{include "whiff_middleware/mako/MakoFile"}}
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
            {{include "whiff_middleware/filePath"}} example.mako {{/include}}
        {{/using}}
    {{/include}}
     
{{/using}}

{{using elsePage}}
    MAKO IS NOT INSTALLED!
{{/using}}
{{/include}}

{{/using}}
{{/include}}
The above example formats the <code>data</code> using the contents of the external file
<code>{{include "whiff_middleware/filePath"}} example.mako {{/include}}</code>:
{{include "whiffhtml"}}
Mako example<br>
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
{{/include}}
The Mako template engine will use the <code>module_directory</code> <code>/tmp</code>
to cache compiled template code (if the directory exists and is writeable).
<p>
Mako is a very fast, powerful, terse, and popular Python text generation
templating engine.  Mako may be superior to WHIFF configuration templates
for formatting complex HTML pages using loops and conditionals.  By using
<code>MakoFile</code> an application may use Mako templates to format text
in place of WHIFF configuration templates.
                                
"""

from whiff.middleware import misc
from whiff import whiffenv
import types
import os

class MakoFile(misc.utility):
    def __init__(self,
                 page,
                 module_directory="",
                 data=None
                 ):
        self.page = page
        self.data = data
        self.module_directory = module_directory
    def __call__(self, env, start_response):
        try:
            from mako.template import Template
        except ImportError:
            raise ImportError, "you must install the mako package from http://www.makotemplates.org/ before using the MakoText middleware"
        # since Mako evaluates python code, disallow rpc tainted environments
        assert not whiffenv.rpc_tainted(env), "security violation: can't evaluate Mako template from rpc tainted environment"
        templatePath = self.param_value(self.page, env).strip()
        makoTemplateData = self.param_json(self.data, env)
        if makoTemplateData is None:
            makoTemplateData = {}
        assert type(makoTemplateData) is types.DictType, "Mako template data must be a mapping of names to values"
        module_directory = self.param_value(self.module_directory, env).strip()
        # convert unicode names to byte strings...
        D = {}
        for (name, value) in makoTemplateData.items():
            D[str(name)] = value
        # xxxx could add additional data validations here...
        # check that the module_directory exists and is writeable
        if module_directory:
            if not os.access(module_directory, os.R_OK | os.W_OK | os.F_OK):
                module_directory = None
        if module_directory:
            mytemplate = Template(filename=templatePath, module_directory=module_directory)
        else:
            mytemplate = Template(filename=templatePath)
        result = mytemplate.render(**D)
        return self.deliver_page(result, env, start_response)

__middleware__ = MakoFile
