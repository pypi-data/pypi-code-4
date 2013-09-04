# Copyright (C) 2012-2013 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import abc
import sys
import pywbem
import tempfile
import subprocess
from textwrap import TextWrapper
from xml.dom.minicompat import NodeList

from LMIUtil import lmi_raise_or_dump_exception

from LMIExceptions import LMINoPagerError

def _is_executable(fpath):
    """
    Returns True, if provided path is executable, False otherwise.

    Arguments:
        fpath -- string containing a path to executable
    """
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

def _which(program):
    """
    Returns a full path of a selected binary.

    Arguments:
        program -- string containing a path to executable
    """
    (fpath, fname) = os.path.split(program)
    if fpath:
        if _is_executable(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if _is_executable(exe_file):
                return exe_file
    return None

def _get_pager_with_params():
    """
    Returns a list containing a binary with its CLI arguments.
    """
    if "PAGER" in os.environ:
        path = _which(os.environ["PAGER"])
        if path:
            return [path]
    for p in ["less", "more"]:
        path = _which(p)
        if not path:
            continue
        elif p == "less":
            return [path, "-S"]
        return [path]
    lmi_raise_or_dump_exception(LMINoPagerError("No default pager found"))
    return []

class LMITextFormatter(object):
    """
    Text formatter class. Used when printing a block of text to output stream.
    """
    def __init__(self, text):
        """
        Constructs a LMITextFormatter object.
        Arguments:
            text -- text to be formatted.
        """
        self._text = text

    def format(self, indent=0, sub_indent=0, width=80, f=sys.stdout, **kwargs):
        """
        Formats a block of text and prints it to the output stream.

        Arguments:
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
            kwargs -- dictionary based arguments, supported arguments:
              separator -- if True, there will be a new line appended after
                the formatted text
        """
        if indent > width:
            return # NOTE: this is wrong!
        wrapper = TextWrapper()
        wrapper.width = width - indent
        wrapper.subsequent_indent = " " * sub_indent
        for l in wrapper.wrap(self._text):
            f.write("%s%s\n" % (" " * indent, l))
        if "separator" in kwargs and kwargs["separator"]:
            f.write("\n")

class LMIFormatter(object):
    """
    Abstract class for XML formatter and MOF formatter.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        stty_dimensions = os.popen("stty size 2> /dev/null", "r").read().split()
        self._width = int(stty_dimensions[1]) if stty_dimensions else 80

    @abc.abstractmethod
    def format(self, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Abstract method, which ought to be overriden in derived classes.

        Arguments:
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        pass

    def fancy_format(self, interactive):
        """
        Formats a block of text. If the LMIShell is running in interactive
        mode, pager will be used, otherwise the output will be written
        to standard output.

        Arguments:
            interactive -- defines, if to use pager or not
        """
        if interactive:
            tmpfile = tempfile.mkstemp()
            f = os.fdopen(tmpfile[0], "w")
            self.format(0, 0, self._width, f)
            f.close()
            subprocess_params = _get_pager_with_params()
            if not subprocess_params:
                return
            subprocess_params.append(tmpfile[1])
            subprocess.call(subprocess_params)
            os.remove(tmpfile[1])
        else:
            self.format(0, 0, self._width)

class LMIXmlFormatter(LMIFormatter):
    """
    XML formatter used for CIMClass.doc() to print pretty verbose help message.
    """
    def __init__(self, xml):
        """
        Constructs a object.

        Arguments:
            xml -- XML element of pywbem.cim_xml.CLASS, retrieved by CIMClass.tocimxml()
        """
        super(LMIXmlFormatter, self).__init__()
        self._xml = xml

    def __format_class_property_content(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a class property.

        Arguments:
            node -- XML element of pywbem.cim_xml.PROPERTY
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        children = node.childNodes
        children_len = len(children)
        for (i, n) in enumerate(children):
            if isinstance(n, pywbem.cim_xml.QUALIFIER):
                self.__format_qualifier(n, indent, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.PROPERTY):
                self.__format_class_property(n, indent, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.PROPERTY_ARRAY):
                self.__format_class_property_array(n, indent, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.METHOD):
                self.__format_method(n, indent, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.VALUE):
                # NOTE: we skip default value for the class
                pass

    def __format_qualifier(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a qualifier.

        Arguments:
            node -- XML element of pywbem.cim_xml.QUALIFIER
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        is_array = isinstance(node.firstChild, pywbem.cim_xml.VALUE_ARRAY)
        val = "[qualifier] %s%s %s" % (node.getAttribute("TYPE"), " []" if is_array else "",
            node.getAttribute("NAME"))
        values = node.childNodes
        if values and isinstance(values[0], pywbem.cim_xml.VALUE_ARRAY):
            val += ": { " + ", ".join(["'" + v.firstChild.nodeValue + "'" for v in values[0].childNodes]) + " }\n"
        else:
            if values:
                val += ": '%s'\n" % values[0].firstChild.nodeValue
        LMITextFormatter(val).format(indent, sub_indent + 4, width, f, separator=True)

    def __format_class_property(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a class property.

        Arguments:
            node -- XML element of pywbem.cim_xml.PROPERETY
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        val = "[property] %s %s" % (node.getAttribute("TYPE"), node.getAttribute("NAME"))
        LMITextFormatter(val).format(indent, sub_indent+4, width, f, separator=True)
        self.__format_class_property_content(node, indent+4, sub_indent, width, f)

    def __format_class_property_array(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a class property array.

        Arguments:
            node -- XML element of pywbem.cim_xml.PROPERTY_ARRAY
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        val = "[property array] %s [] %s" % (node.getAttribute("TYPE"), node.getAttribute("TYPE"))
        LMITextFormatter(val).format(indent, sub_indent+4, width, f, separator=True)
        self.__format_class_property_content(node, indent+4, sub_indent, width, f)

    def __format_class_property_reference(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a class property reference.

        Arguments:
            node -- XML element of pywbem.cim_xml.PROPERTY_REFERENCE
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        val = "[property ref] %s %s" % (node.getAttribute("REFERENCECLASS"), node.getAttribute("NAME"))
        LMITextFormatter(val).format(indent, sub_indent+4, width, f, separator=True)
        self.__format_class_property_content(node, indent+4, sub_indent, width, f)

    def __format_instance_property(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a instance property.

        Arguments:
            node -- XML element of pywbem.cim_xml.PROPERTY
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        val = node.firstChild
        prop = "[property] %s %s%s" % (node.getAttribute("TYPE"), node.getAttribute("NAME"),
            " = '%s'" % val.firstChild.nodeValue if val else "")
        LMITextFormatter(prop).format(indent, sub_indent+4, width, f, separator=True)

    def __format_instance_property_array(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a instance property array.

        Arguments:
            node -- XML element of pywbem.cim_xml.PROPERTY_ARRAY
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        prop = "[property array] %s [] %s" % (node.getAttribute("TYPE"), node.getAttribute("NAME"))
        val = node.firstChild
        if val:
            prop += " = { " + ", ".join(["'" + v.firstChild.nodeValue + "'" for v in val.childNodes]) + " }"
        LMITextFormatter(prop).format(indent, sub_indent+4, width, f, separator=True)

    def __format_instance_property_reference(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a instance property reference.

        Arguments:
            node -- XML element of pywbem.cim_xml.PROPERTY_REFERENCE
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        val = "[property ref] %s %s" % (node.getAttribute("REFERENCECLASS"), node.getAttribute("NAME"))
        LMITextFormatter(val).format(indent, sub_indent+4, width, f, separator=True)

    def __format_method(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a class method.
        Arguments:
            node -- XML element of pywbem.cim_xml.METHOD
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        qualifiers = [x for x in node.childNodes if isinstance(x, pywbem.cim_xml.QUALIFIER)]
        parameters = [x for x in node.childNodes if isinstance(x, pywbem.cim_xml.PARAMETER)]
        parameters_arr = [x for x in node.childNodes if isinstance(x, pywbem.cim_xml.PARAMETER_ARRAY)]
        parameters_ref = [x for x in node.childNodes if isinstance(x, pywbem.cim_xml.PARAMETER_REFERENCE)]
        parameters_ref_arr = [x for x in node.childNodes if isinstance(x, pywbem.cim_xml.PARAMETER_REFARRAY)]
        has_args = parameters != [] or parameters_arr != [] or parameters_ref != [] or parameters_ref_arr != []
        val = "[method] %s %s%s" % (node.getAttribute("TYPE"), node.getAttribute("NAME"), "(...)" if has_args else "()")
        LMITextFormatter(val).format(indent, sub_indent, width, f, separator=True)
        for q in qualifiers:
            self.__format_qualifier(q, indent+4, sub_indent+4, width, f)
        for p in parameters:
            val = "[param] %s %s" % (p.getAttribute("TYPE"), p.getAttribute("NAME"))
            LMITextFormatter(val).format(indent+4, sub_indent+4, width, f, separator=True)
        for p in parameters_arr:
            val = "[param array] %s (ref) %s" % (p.getAttribute("TYPE"), p.getAttribute("NAME"))
            LMITextFormatter(val).format(indent+4, sub_indent+4, width, f, separator=True)
        for p in parameters_ref:
            val = "[param ref] %s (ref) %s" % (p.getAttribute("REFERENCECLASS"), p.getAttribute("NAME"))
            LMITextFormatter(val).format(indent+4, sub_indent+4, width, f, separator=True)
        for p in parameters_ref_arr:
            val = "[param ref array] %s (ref) %s" % (p.getAttribute("REFERENCECLASS"), p.getAttribute("NAME"))
            LMITextFormatter(val).format(indent+4, sub_indent+4, width, f, separator=True)

    def __format_class(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a class.

        Arguments:
            node -- XML element of pywbem.cim_xml.CLASS
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        LMITextFormatter("Class: %s" % node.getAttribute("NAME")).format(indent, sub_indent, width, f)
        LMITextFormatter("SuperClass: %s" % node.getAttribute("SUPERCLASS")).format(indent+4, sub_indent, width, f)
        for n in node.childNodes:
            if isinstance(n, pywbem.cim_xml.QUALIFIER):
                self.__format_qualifier(n, indent+4, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.PROPERTY):
                self.__format_class_property(n, indent+4, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.PROPERTY_ARRAY):
                self.__format_class_property_array(n, indent+4, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.PROPERTY_REFERENCE):
                self.__format_class_property_reference(n, indent+4, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.METHOD):
                self.__format_method(n, indent+4, sub_indent, width, f)

    def __format_instance(self, node, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats an instance.

        Arguments:
            node -- XML element of pywbem.cim_xml.VALUE_NAMEDINSTANCE
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        instance = node.firstChild.nextSibling
        LMITextFormatter("Instance of %s" % instance.getAttribute("CLASSNAME")).format(indent, sub_indent, width, f)
        for n in instance.childNodes:
            if isinstance(n, pywbem.cim_xml.PROPERTY):
                self.__format_instance_property(n, indent+4, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.PROPERTY_ARRAY):
                self.__format_instance_property_array(n, indent+4, sub_indent, width, f)
            elif isinstance(n, pywbem.cim_xml.PROPERTY_REFERENCE):
                self.__format_instance_property_reference(n, indent+4, sub_indent, width, f)

    def format(self, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a XML object and prints it to the output stream.

        Arguments:
            indent -- number of spaces to indent the text block
            sub_indent -- number of spaces for the second and other lines
                of the text block
            width -- total text block width
            f -- output stream
        """
        if isinstance(self._xml, pywbem.cim_xml.CLASS):
            self.__format_class(self._xml, indent, sub_indent, width, f)
        elif isinstance(self._xml, pywbem.cim_xml.VALUE_NAMEDINSTANCE):
            self.__format_instance(self._xml, indent, sub_indent, width, f)

class LMIMofFormatter(LMIFormatter):
    """
    MOF formatter used for CIMInstance.doc() to print pretty verbose help message.
    """
    def __init__(self, mof):
        """
        Constructs a object.

        Arguments:
            mof -- string containing a MOF representation of a object
        """
        super(LMIMofFormatter, self).__init__()
        self._mof = mof

    def format(self, indent=0, sub_indent=0, width=80, f=sys.stdout):
        """
        Formats a MOF object and prints it to the output stream.
        """
        f.write(self._mof)
