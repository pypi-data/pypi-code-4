#!/usr/bin/python
"""
Python filter to process Stata commands from Pandoc.

See the readme for pan.

"""

import itertools
import functools
import json
import os
import envoy
import sys
from pan.pandoc import toJSONFilter
import uuid

# default line length for stata output
LINESIZE = 100



format_strings = {
    "latex": """\\vskip .5\\baselineskip
\\needspace{{
{output_length}
\\baselineskip}}
\\marginnote[2\\baselineskip]{{
{commentary}
}}
\\begin{{Verbatim}}[label={{{label}}}, commandchars={commandchars}, formatcom=\\color{{Green}}]
\label{{{label}}}
{output}
\\end{{Verbatim}}""",

    "html": """<label>{commentary}
<code class="stata">
{output}
</code></label>
""",

"txt": """
{commentary}

{output}
"""

}





def stata(key, value, format, **meta):

    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        stata = "stata" in classes
        run = "run" in classes
        hide = "hide" in classes
        commentary = dict(keyvals).get("commentary", "")
        label = dict(keyvals).get("label", "")
        title = dict(keyvals).get("title", "")

        if hide:
            return []

        if stata and not run:
            output = code
            output_length = len(code.split("\n"))

        if stata and run:
            code = code.replace(">>>", """di ">>>" """)
            code = """capture cd {}\nset linesize {}\ndi ">>>" \n""".format(os.getcwd(), LINESIZE) + code
            result = envoy.run('statpipe', data=code)

            # hide the change dir command
            stataoutput = result.std_out.split(">>>")[-1]
            lines = stataoutput.split("\n")

            # hide captures
            lines = [i for i in lines if not i.startswith(". cap:")]
            hide_lines = set(json.loads(dict(keyvals).get("hide_lines", "[]")))
            lines = [x for i, x in enumerate(lines) if i not in hide_lines]
            output = "\n".join(lines)
            output_length = len(lines)

            if not output:
                # only add errors if there is no output from statpipe
                output += result.std_err

        d = {
                'output': output,
                'output_length': output_length,
                'commentary': commentary,
                'title': title,
                'id': ident or uuid.uuid1().hex,
                'label':  label,
                'commandchars': r'\\\{\}'
        }

        if format in format_strings.keys():
            return {"Para":[{"RawInline": [format,
                format_strings.get(format).format(**d)]}]}
        else:
            return {"CodeBlock": [[ident, classes, keyvals], output]}

if __name__ == "__main__":
    toJSONFilter(stata)
