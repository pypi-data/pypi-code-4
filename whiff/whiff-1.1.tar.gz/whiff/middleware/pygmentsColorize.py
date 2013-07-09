
"""
Colorize text as html using pygments
"""

whiffCategory = "library"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/pygmentsColorize - colorize programming language text
{{/include}}

The <code>whiff_middleware/pygmentsColorize</code>
middleware colorizes a programming language
text fragment.  This middleware will not work unless
the Pygments software is installed separately for the
Python installation.  The Pygments installation is not
automatic.  The page using this module must also
include the <code>pygmentsCss</code> stylesheet.

{{include "example"}}
{{using targetName}}pygmentsColorize{{/using}}
{{using page}}

{{include "whiff_middleware/pygmentsColorize"}}
    {{using lexer}}java{{/using}}
    {{using page}}
import org.sakaiproject.user.api.UserDirectoryService;
import org.sakaiproject.tool.api.SessionManager;

/**
 * <p>
 * AliasServiceTest extends the db alias service providing the dependency injectors for testing.
 * </p>
 */
public class AliasServiceTest extends DbAliasService
{
	/**
	 * @return the MemoryService collaborator.
	 */
	protected MemoryService memoryService()
	{
		return null;
	}

	/**
	 * @return the ServerConfigurationService collaborator.
	 */
	protected ServerConfigurationService serverConfigurationService()
	{
		return null;
	}
	etcetera....
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

from pygments import highlight  # this middleware requires Pygments!
from pygments.lexers import get_lexer_by_name
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter


# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver
# environment key which may name the css class
from whiff.middleware.pygmentsCss import envCssClassName
from whiff.middleware.pygmentsCss import defaultCssClassName
# environment key which may name the pygments lexer
envLexerName = "pygmentsCss.lexer"

class pygmentsColorize(misc.utility):
    def __init__(self, page, lexer=None, cssClass=None, filename=None):
        self.page = page
        self.lexer = lexer
        self.cssClass = cssClass
        self.filename = filename
    def __call__(self, env, start_response):
        # IF unquote IN ENVIRONMENT, UNQUOTE THE PAGE FOR HTML
        unquoteIt = env.get("unquote")
        cssClassName = lexerName = None
        # find css class
        if self.cssClass:
            cssClassName = self.param_value(self.cssClass, env)
        else:
            # check for environment entry
            cssClassName = env.get(envCssClassName)
        if cssClassName is None:
            cssClassName = defaultCssClassName
        # find lexer (no default)
        lexer = None
        if self.lexer:
            lexerName = self.param_value(self.lexer, env)
        else:
            # check environment
            lexerName = env.get(envLexerName)
        if lexerName is None and self.filename:
            # try to use file name if given
            filename = self.param_value(self.filename, env).strip()
            lexer = get_lexer_for_filename(filename)
        if lexerName is None and lexer is None:
            raise ValueError, "lexer name or recognized file name must be specified either as a require or in the environment"
        code = self.param_value(self.page, env)
        if not lexer:
            lexer = get_lexer_by_name(lexerName, stripall=True, encoding="utf-8")
        formatter = HtmlFormatter(linenos=False, cssclass=cssClassName)
        if unquoteIt:
            code = resolver.unquote(code)
        payload = highlight(code, lexer, formatter)
        start_response("200 OK", [('Content-Type', 'text/css')])
        return [payload]

__middleware__ = pygmentsColorize

def test():
    app = pygmentsColorize("<h1>hello</h1>", None, "cssClass", "http://x.y.z/www/local/com/test.html")
    print "test returns", app({}, misc.ignore)

if __name__=="__main__":
    test()
    
