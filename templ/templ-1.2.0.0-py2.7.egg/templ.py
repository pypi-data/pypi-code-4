#!/usr/bin/python
"""
Copyright 2013 Brian Mearns

This file is part of templ.

templ is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

templ is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with templ.  If not, see <http://www.gnu.org/licenses/>.

"""
import teval
import texec
import types
import ttypes
import texceptions
import tstreams
import stack as tStack
import io
import os
import filepos as tFilepos

#Needed for main
import tbuiltin
import sys
import errno
import version
import codecs


TOKEN_EOI = 0
TOKEN_SPACE = 1
TOKEN_OCUR = 2
TOKEN_CCUR = 3
TOKEN_SLASH = 4
TOKEN_QUOTE = 5
TOKEN_TEXT = 6
TOKEN_COMMENT = 7
TOKEN_OEMBED = 8
TOKEN_CEMBED = 9


STMT_EOI = 0
STMT_TEXT = 1
STMT_LIST = 2
STMT_CEMBED = 3

#             LF    VT      FF      CR    CR+LF   NEL     LS        PS
LINEBREAKS = ("\n", "\x0B", "\x0C", "\r", "\r\n", u"\x85", u"\u2028", u"\u2029")

        
class TemplateProcessingError(texceptions.TemplateException):
    def __init__(self, cause, filepos=None):
        super(TemplateProcessingError, self).__init__(cause, filepos)

    def __str__(self):
        if self.filepos is None:
            filepos = ""
        else:
            filepos = " " + str(self.filepos)
        return "Error%s: %s" % (filepos, self.message)

class TemplateSyntaxError(TemplateProcessingError):
    pass


def process(istream, ostream, scope=None, iname="<input-stream>", debug=False):
    stack = tStack.Stack(scope)
    processWithStack(istream, ostream, stack, iname, debug)

def processWithStack(istream, ostream, stack, iname="<input-stream>", debug=False):

    if not isinstance(istream, tstreams.TemplateInputStream):
        istream = tstreams.TemplateInputStream(istream, iname)

    try:
        while True:
            stmt, value, filepos = parse(istream)

            if stmt == STMT_EOI:
                return

            #In text mode (i.e., at the top level), CEMBED is meaningless. OEMBED is already returned by
            # the parser as TEXT.
            elif stmt in (STMT_TEXT, STMT_CEMBED) :
                assert(isinstance(value, basestring)), repr(value)
                if not isinstance(value, unicode):
                    # We assume any strings generated internally are latin-1.
                    # If they came from the input, then they would be unicode objects.
                    value = unicode(value, "latin1")
                try:
                    ostream.write(value)
                except UnicodeEncodeError, e:
                    raise texceptions.TemplateException(e, filepos)
                    

            elif stmt == STMT_LIST:
                #Evaluate it.
                res = teval.evalExpression(value, ostream, stack)
                assert(isinstance(res, ttypes.TType))

                #At the top level, NULL is an empty string.
                # This is necessary so that all we have to do is wrap something in {v ...} to supress
                # the output at the top level.
                if isinstance(res, ttypes.Null):
                    pass
                elif isinstance(res, ttypes.String):
                    string = res.str
                    assert(isinstance(string, basestring)), repr(string)
                    if not isinstance(string, unicode):
                        # We assume any strings generated internally are latin-1.
                        # If they came from the input, then they would be unicode objects.
                        string = unicode(string, "latin1")

                    try:
                        ostream.write(string)
                    except UnicodeEncodeError, e:
                        raise texceptions.TemplateException(e, filepos)
                else:
                    raise texceptions.TemplateTypeException("Top level expression resulted in non-String value.", res.filepos, got=res)

    except texceptions.TemplateException, e:
        if debug:
            raise
        raise TemplateProcessingError(e, e.filepos)
        



def parse(istream):
    """
    Top level parser, handles both TEXT and LIST expressions (well, it delegates).
    """
    plaintext = None
    ptstart = None
    while True:
        token, text, filepos = lex(istream)

        if token == TOKEN_EOI:
            if plaintext is not None:
                #Strip final EOL.
                longestEol = 0
                #Need to find the longest EOL that it ends with. For instance, if it
                # ends in \r\n, it will match \n, but we need to remove 2 chars, not 1.
                for eol in LINEBREAKS:
                    if plaintext.endswith(eol) and len(eol) > longestEol:
                        longestEol = len(eol)
                if longestEol > 0:
                    plaintext = plaintext[:-longestEol]
                return (STMT_TEXT, plaintext, ptstart)
            else:
                return (STMT_EOI, None, filepos)

        #We're operating in TEXT mode, so most of these tokens have no special meaning.
        elif token in (TOKEN_TEXT, TOKEN_SPACE, TOKEN_CCUR, TOKEN_QUOTE, TOKEN_COMMENT, TOKEN_OEMBED):
            if plaintext is None:
                plaintext = ""
                ptstart = filepos
            plaintext += text

        elif token == TOKEN_CEMBED:
            #If we've buffered any text, return that first.
            if plaintext is not None:
                #And unget the CEMBED
                istream.unget(text)
                return (STMT_TEXT, plaintext, ptstart)
            else:
                return (STMT_CEMBED, text, filepos)

        #In text mode, we use slash to escape curly braces.
        elif token == TOKEN_SLASH:
            content = ""

            #See what it's escaping.
            token, text, dummy = lex(istream)

            #Slashes aren't needed or used to escape slashes, so if it's a slash followed by a slash,
            # then the first one wasn't an escape, it's just text. But now we've got another slash
            # that might be escaping...
            while token == TOKEN_SLASH:
                content += '\\'
                token, text, dummy = lex(istream)

            if token in (TOKEN_OCUR, TOKEN_CCUR):
                #Write the curly brace, it's been escaped.
                content += text

            #Otherwise, slash has no special meaning, treat it as text, so output both the slash
            # and the text.
            else:
                content += '\\' + text

            if plaintext is None:
                plaintext = ""
                ptstart = filepos
            plaintext += content


        #Start of an expression
        elif token == TOKEN_OCUR:
            if plaintext is not None:
                #Unget start of expression
                istream.unget(text)
                return (STMT_TEXT, plaintext, ptstart)
                
            expr = parseExpr(istream, filepos)
            assert(isinstance(expr, ttypes.List))
            return (STMT_LIST, expr, filepos)




def parseExpr(istream, filepos):
    """
    We've already read the opening curly brace, this has to parse the remainder of the expression
    up to an including the closing curly brace, and return a TType List it represents. Do NOT evaluate
    anything here, just build the expression tree.
    """
    elements = []
    myfilepos = filepos
    cur = None
    curstart = None
    while True:
        token, text, filepos = lex(istream)

        if token == TOKEN_EOI:
            raise TemplateSyntaxError("Input ended with expression unterminated.", myfilepos)

        #White space is a separator, otherwise ignored.
        elif token == TOKEN_SPACE:
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
                cur = None
                curstart = None

        #Slash has no special meaning here, it's just text.
        elif token in (TOKEN_TEXT, TOKEN_SLASH):
            if cur is None:
                cur = ""
                curstart = filepos
            cur += text

        #Quoted strings just count as text, appended to existing text.
        elif token == TOKEN_QUOTE:
            if cur is None:
                cur = ""
                curstart = filepos
            cur += parseStringLiteral(istream, filepos)

        # EOL comment, treated as whitespace.
        elif token == TOKEN_COMMENT:
            #Its also a punctuator, so if we were building a string, complete it.
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
                cur = None
                curstart = None

            comment = text
            while True:
                c = istream.read(1)
                if len(c) == 0:
                    raise TemplateSyntaxError("Input ended with expression unterminated.", myfilepos)

                comment += c
                if any(comment.endswith(lb) for lb in LINEBREAKS):
                    unget = True
                    #Found a linebreak. Now find the longest matching linebreak.
                    while any(comment.endswith(lb) for lb in LINEBREAKS):
                        c = istream.read(1)
                        if len(c) == 0:
                            unget = False
                            break
                        comment += c

                    #Unget the last char (the non-EOL char)
                    if unget:
                        istream.unget(comment[-1])
                        comment = comment[:-1]
                    break

        #Embedded template.
        elif token == TOKEN_OEMBED:
            #Its also a punctuator, so if we were building a string, complete it.
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
                cur = None
                curstart = None

            embedded = ["'"]
            embeddedStart = filepos

            #This puts us back at the top level, so start parsing at the top level.
            while True:
                stmt, value, filepos = parse(istream)

                if stmt == STMT_EOI:
                    raise TemplateSyntaxError("Input ended with expression unterminated.", myfilepos)

                elif stmt == STMT_TEXT:
                    embedded.append(ttypes.String(value, filepos))

                elif stmt == STMT_CEMBED:
                    break

                elif stmt == STMT_LIST:
                    assert(isinstance(value, ttypes.List))
                    embedded.append(value)

            elements.append(ttypes.List(embedded, embeddedStart))            

        elif token == TOKEN_CEMBED:
            raise TemplateSyntaxError("Input >>> in expression. This is a reserved token inside expressions, to use it as a string, it must be quoted.", myfilepos)

        elif token == TOKEN_CCUR:
            #End of expression.
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
            return ttypes.List(elements, myfilepos)

        elif token == TOKEN_OCUR:
            #Start of another expression.
            if cur is not None:
                elements.append(ttypes.String(cur, curstart))
                cur = None
                curstart = None

            expr = parseExpr(istream, filepos)
            assert(isinstance(expr, ttypes.List))
            elements.append(expr)

        else:
            raise AssertionError("Unknown token %d" % token)


def parseStringLiteral(istream, filepos):
    string = ""
    while True:
        c = istream.read(1)
        if len(c) == 0:
            raise TemplateSyntaxError("Input ended with string-literal unterminated.", filepos)

        elif c == '"':
            return string

        elif c == '\\':
            c = istream.read(1)
            if len(c) == 0:
                raise TemplateSyntaxError("Input ended with string-literal unterminated.", filepos)

            #Escape always just means "include the next character in the string."
            string += c

        else:
            string += c


def lex(istream):
    filepos = istream.getPosition()
    c = istream.read(1)

    if len(c) == 0:
        #Reached end of input.
        return (TOKEN_EOI, "", filepos)

    elif c.isspace():
        #Consume whitespace strings.
        space = c
        while True:
            c = istream.read(1)
            if len(c) == 0:
                break
            elif c.isspace():
                space += c
            else:
                #Unget.
                istream.unget(c)
                break
        return (TOKEN_SPACE, space, filepos)

    elif c == "{":
        return (TOKEN_OCUR, c, filepos)

    elif c == "}":
        return (TOKEN_CCUR, c, filepos)

    elif c == '\\':
        return (TOKEN_SLASH, c, filepos)

    elif c == '"':
        return (TOKEN_QUOTE, c, filepos)

    elif c == '%':
        return (TOKEN_COMMENT, c, filepos)

    elif c == '<':
        #Check for embed.
        text = '<'
        while True:
            c = istream.read(1)
            if len(c) == 0:
                #EOI, so it was not an embed, so just return it as text.
                return (TOKEN_TEXT, text, filepos)
            elif c == '<':
                text += c
                if text == "<<<":
                    #Embed!
                    return (TOKEN_OEMBED, text, filepos)
            else:
                #Non '<', so not an embed. Unget that last non-'<' char.
                istream.unget(c)
                #And it's just text.
                return (TOKEN_TEXT, text, filepos)

    elif c == '>':
        #Check for embed.
        text = '>'
        while True:
            c = istream.read(1)
            if len(c) == 0:
                #EOI, so it was not an embed, so just return it as text.
                return (TOKEN_TEXT, text, filepos)
            elif c == '>':
                text += c
                if text == ">>>":
                    #Embed!
                    return (TOKEN_CEMBED, text, filepos)
            else:
                #Non '>', so not an embed. Unget that last non-'>' char.
                istream.unget(c)
                #And it's just text.
                return (TOKEN_TEXT, text, filepos)

    else:
        #Plaintext char
        #Consume all.
        text = c
        while True:
            c = istream.read(1)
            if len(c) == 0:
                break
            elif c.isspace() or c in ('{', '}', '\\', '"', '%', '>'):
                #Unget.
                istream.unget(c)
                break
            else:
                text += c
        return (TOKEN_TEXT, text, filepos)
            



def printVersion(ostream):
    ostream.write("templ v{version} - {datestr}\n\n".format(version=version.string(), datestr=version.datestr()))

def printUsage(ostream, argv=sys.argv):
    ostream.write(
"""Usage: {PROG} [options] [TEMPLATE_FILE [OUTFILE]]
   or: {PROG} [options] - [OUTFILE]

""".format(PROG=argv[0]))


def printHelp(ostream, argv=sys.argv):
    printVersion(ostream)
    printUsage(ostream, argv)
    ostream.write(
"""Processes TEMPLATE_FILE through the templ processor, writing the output to
OUTFILE. In the second usage, the use of "-" as the TEMPLATE_FILE indicates
that the template should be read from STDIN. This is also the default if
TEMPLATE_FILE is not specified. Likewise, a dash can be used for OUTFILE to
indicate that output should be written to STDOUT, which is also the default if
OUTFILE is not given.

Options:
 -s, --set NAME [VALUE]         Adds a symbol named NAME to the global scope
                                with a String type value given by VALUE. If
                                VALUE is not given, a NULL value is used.

 -b, --binary                   Opens the input and output files in binary
                                mode, when possible. This is not possible for
                                standard streams (STDIN or STDOUT).

 -e, --in-enc ENCODING          Specify the encoding to use when reading the 
                                input. Default is Latin-1 (one char per
                                octet read). Other options include UTF-8,
                                UTF-16, and UTF-32. Use --help-enc for more
                                details on encoding.

 -E, --out-enc ENCODING         Specify the encoding to use when writing to
                                the output. Default is Latin-1 (sometimes
                                called "extended ASCII", this is one octet
                                per char, chars with values greater than 255
                                will cause an error). Other options include
                                UTF-8, UTF-16, and UTF-32. Use --help-enc for
                                more details on encoding.

Misc Options:
 --debug                        Enable debug output.

 -V, --version                  Print the version string and exit.

 --usage                        Print a brief usage message and exit.

 --help-enc                     Print help on encoding.

 --help                         Print this help menu.



Copyright {COPYRIGHT} Brian Mearns. Program licensed under GNU AGPLv3.

For more information about this product see:
            <https://bitbucket.org/bmearns/templ/>.
""".format(COPYRIGHT=version.COPYRIGHT)
    )

def printEncodingHelp(ostream, argv=sys.argv):
    printVersion(ostream)
    ostream.write(
"""
Encoding:

For most English-language templates, the default encoding, Latin-1, will work
fine. ASCII is a subset of Latin-1 for codepoints 0-127, and Latin-1 adds a
number of common accented characters in the range from 128 through 255.

Latin-1 also works well if you plan to generate binary output, because octet
values will not be changed by the output encoder. For instance in Latin-1, the
templ code...
    {chr 144}
...will produce a single octet of output, with octet value 0x90. On the other
hand, if the output encoding is set to UTF-8, the same code will produce two
octets of output, the first with value 0xC2, then second with value 0x90.

For input encoding, the default of Latin-1 is usually sufficient for most
templates, including those stored in ASCII, Latin-1, or UTF-8. Even if the
template is stored in UTF-8, the Latin-1 input encoding will simply read each
byte as a single char and will not produce any encoding errors. Since all
characters that are of significance to templ itself are in the ASCII subset
anyway (a subset of both Latin-1 and UTF-8), templ will not have any trouble
understanding the input.

However, there are two likely sources of problems using Latin-1 input
encoding for a UTF-8 template. First, the string length of text that
originated in the template may not be correct. For instance, if the template
includes a unicode inverted question mark (codepoint U+00BF), this will be
stored as two octets in the UTF-8 encoded template file (0xC2 0xBF). The
string only contains one character (U+00BF) in UTF-8, but when read with
Latin-1 input encoding, it will result in a string with two chracters (\\xC2
and \\xBF).

The second potential issue depends on the output encoding used. If you use
Latin-1 output encoding, it will work fine (other than as discussed above):
the exact octets that appeared in the input template will also appear in the
output, which will be interpretted correctly by a UTF-8 reader. However, if
you use any of the UTF encodings for output, then each octet in the input
template could be encoded to multiple octets in the output. For instance, if
the input template once again contains unicode character U+00BF (inverted
question mark) in UTF-8, it will be read in Latin-1 as a two-character string,
with codepoint \\u00C2 and \\u00BF. If this is then written out using UTF-8
encoding, it will produce four octets in total: the character \\u00C2 (Latin
capital letter A with circumflex) will be encoded as two octets as
0xC3 0x82, and the character \\u00BF (inverted question mark) will once again
be encoded as two octets 0xC2 0xBF.

The best solution is to use the correct input encoding based on how the
template is stored. If it uses only ASCII characters and is stored using ASCII
encoding, then the default will work fine. Likewise, if it is a binary file
which contains non-textual binary octets, the default encoding will work well.
But if the file is stored in any other encoding (UTF-8 being common for
non-English language documents), then specify the same as the input encoding
when invoking templ.

The output encoding is really just a matter of how you want to store the
output. If the output only contains ASCII characters, or if it contains
non-textual binary octets, the default encoding, Latin-1, should work fine.
However, if you attempt to output any string which includes a codepoint
greater than 255, then Latin-1 encoding will not work and you will get an
error.


Copyright {COPYRIGHT} Brian Mearns. Program licensed under GNU AGPLv3.

For more information about this product see:
            <https://bitbucket.org/bmearns/templ/>.
""".format(COPYRIGHT=version.COPYRIGHT)
    )

def main():

    templates = []
    infile = None
    outfile = None
    #Our initial scope.
    globs = texec.getGlobalScope()
    debug = False
    binary = False
    in_enc = "latin"
    out_enc = "latin"

    i = 1
    argc = len(sys.argv)
    while i < argc:
        arg = sys.argv[i]
        i += 1
        if arg in ("-h", "-?", "/?", "--help"):
            printHelp(sys.stdout, sys.argv)
            return (0)

        if arg in ("--help-enc",):
            printEncodingHelp(sys.stdout, sys.argv)
            return (0)

        elif arg in ("-V", "--version"):
            printVersion(sys.stdout)
            return (0)

        elif arg in ("--usage", ):
            printUsage(sys.stdout, sys.argv)
            return (0)

        elif arg in ("--debug", ):
            debug = True

        elif arg in ("-b", "--binary", ):
            binary = True

        elif arg in ("-s", "--set"):
            if i == argc:
                sys.stderr.write("%s: Error: Missing required parameter for option %s.\n" % (sys.argv[0], arg))
                sys.stderr.write("%s: Try `%s --help`\n" % (sys.argv[0], sys.argv[0]))
                return (errno.EINVAL)
            else:
                name = sys.argv[i]
                i += 1
                fp = tFilepos.CommandLineFilepos.new(i)
                if i < argc:
                    value = sys.argv[i]
                    value = ttypes.String(value, filepos=fp)
                    i += 1
                else:
                    value = ttypes.Null(filepos=fp)
                globs[name] = value

        elif arg in ("-e", "--in-enc"):
            if i == argc:
                sys.stderr.write("%s: Error: Missing required parameter for option %s.\n" % (sys.argv[0], arg))
                sys.stderr.write("%s: Try `%s --help`\n" % (sys.argv[0], sys.argv[0]))
                return (errno.EINVAL)
            else:
                in_enc = sys.argv[i]
                i += 1

        elif arg in ("-E", "--out-enc"):
            if i == argc:
                sys.stderr.write("%s: Error: Missing required parameter for option %s.\n" % (sys.argv[0], arg))
                sys.stderr.write("%s: Try `%s --help`\n" % (sys.argv[0], sys.argv[0]))
                return (errno.EINVAL)
            else:
                out_enc = sys.argv[i]
                i += 1


        else:
            if infile is None:
                infile = arg
            elif outfile is None:
                outfile = arg
            else:
                sys.stderr.write("%s: Error: Unexpected argument \"%s\".\n" % (sys.argv[0], arg))
                sys.stderr.write("%s: Try `%s --help`\n" % (sys.argv[0], sys.argv[0]))
                return (errno.EINVAL)
                

    istream = None
    ostream = None
    try:
        if (infile is None) or (infile == "-"):
            iname = "<stdin>"
            istream = sys.stdin
        else:
            iname = infile
            mode = "r"
            if binary:
                mode += "b"
            istream = open(iname, mode)
        try:
            istream = codecs.getreader(in_enc)(istream)
        except LookupError, e:
            sys.stderr.write("Error: unknown encoding for --in-enc.\n")
            try: istream.close()
            except: pass
            return -1

        if (outfile is None) or (outfile == "-"):
            ostream = sys.stdout
        else:
            mode = "w"
            if binary:
                mode += "b"
            ostream = open(outfile, mode)
        try:
            ostream = codecs.getwriter(out_enc)(ostream)
        except LookupError, e:
            sys.stderr.write("Error: unknown encoding for --out-enc.\n")
            try: ostream.close()
            except: pass
            return -1
        ostream = tstreams.TemplateStreamOutputStream(ostream)

        try:
            #Invoke the templ processor.
            process(istream, ostream, globs, iname, debug)

        except TemplateProcessingError, e:
            #Catch and pretty-print errors found in the template.
            if debug:
                raise

            try: istream.close()
            except Exception: pass
            try: ostream.close()
            except Exception: pass

            sys.stderr.write(str(e) + "\n")
            return (-1)

        try: istream.close()
        except Exception: pass
        try: ostream.close()
        except Exception: pass

    except IOError, e:
        if debug:
            raise e

        if istream is not None:
            try: istream.close()
            except Exception: pass
        if ostream is not None:
            try: ostream.close()
            except Exception: pass

        sys.stderr.write("An IO Error occurred: %s\n" % str(e))
        return (errno.EIO)

if __name__ == "__main__":
    ec = main()
    sys.exit(ec)

