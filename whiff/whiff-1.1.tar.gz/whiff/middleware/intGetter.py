"""
Integer "get" operation for testing list dropdown (loadList).
"""

whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/intGetter - get int value
{{/include}}

The <code>whiff_middleware/intGetter</code>
middleware is a test <code>getter</code> for
use with the <code>loadList</code> middleware.
"""

from whiff.middleware import loadList

__middleware__ = loadList.exampleGetter
