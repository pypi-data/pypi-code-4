#!/usr/bin/python

import os
import envoy
import sys
from pan.pandoc import toJSONFilter


def stata(key, value, format, **meta):

    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        stata = "stata" in classes
        run = "run" in classes
        hide = "hide" in classes


        if stata and not run:
            if hide:
                return []
            return {'CodeBlock': [[ident, classes, keyvals], code]}


        if stata and run:
            code = "capture cd {}\n".format(os.getcwd()) + code
            result = envoy.run('statpipe', data=code)

            # hide the change dir command
            lines = result.std_out.split("\n")[2:]
            # hide captures
            lines = [i for i in lines if not i.startswith(". cap:")]
            log = "\n".join(lines) + result.std_err

            # per-output-format formatting here, e.g. colors
            if hide:
                return []
            if format=="latex":
                commentary = dict(keyvals).get("commentary", "")
                commentary_marginnote = """
\\vskip .5\\baselineskip
\\needspace{%s\\baselineskip}
\\marginnote[2\\baselineskip]{%s}""" % (len(log.split("\n")), commentary)

                title = dict(keyvals).get("title", "")

                return [
                    {"Para":[{"RawInline":
                        ["latex",
                            """
%s
\\begin{Verbatim}[label=%s, commandchars=\\\\\\{\\}, formatcom=\\color{Green}]
\label{%s}
%s
\\end{Verbatim}""" % (commentary_marginnote, title, ident, log)]}]}]

            return [{'CodeBlock': [[ident, classes, keyvals], log]}]



if __name__ == "__main__":
    toJSONFilter(stata)
