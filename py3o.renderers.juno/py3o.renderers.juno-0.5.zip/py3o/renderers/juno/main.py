import jpype
from jpype import startJVM
#from jpype import java
from jpype import JPackage
#, JavaException

import os
import logging
import pkg_resources

log = logging.getLogger(__name__)

formats = dict(
        WORD97='MS Word 97', # 97 & 2000
        WORD2003='MS Word 2003 XML',
        PDF='writer_pdf_Export',
        DOCBOOK='DocBook File',
        HTML='HTML',
        )

# define some hard coded jar resource we will try to find when starting the JVM
ureitems = ["juh.jar", "jurt.jar", "ridl.jar", "unoloader.jar", "java_uno.jar"]
basisitems = ["unoil.jar",]

def get_oo_context(office_version):
    """returns a dict with the java_classpath_sep, ure_subpath
    and oooclasses_subpath key pointing the (hopefully) correct sub paths
    for the current running plateform. The implementer still needs
    to provide the real base path for his plateform elsewhere in its
    code though...

    @param office_version: the version number of the desired
    OpenOffice/LibreOffice
    @type office_version: string
    """

    context = dict()

    if os.name in ('nt', 'os2', 'ce'): # Windows
        # tested to work with OpenOffice 3.2, we need to confirm
        # it works with LibreOffice
        context['java_classpath_sep'] = ";"
        context['ure_subpath'] = os.path.join('URE', 'java')
        context['oooclasses_subpath'] = os.path.join(
                "Basis", "program", "classes")

    else:
        context['java_classpath_sep'] = ":"
        # TODO: do that properly
        # for now, hard-code the stuff on CentOS5.5 x86_64 with OOo 3.1
        # this is also working on RedHat RHEL 5 and on Ubuntu
        context['ure_subpath'] = os.path.join('ure', 'share', 'java')
        context['oooclasses_subpath'] = os.path.join("program", "classes")

    return context


def start_jvm(jvm, oobase, urebase, office_version, max_mem):
    """this small function should be called only once. At the beginning
    of your program.
    It takes care of starting the JVM that will be used by our
    convertor library with our requirements in terms of
    classpath and memory usage

    returns nothing

    @param jvm: the jvm path to use :
    ie c:/Program Files/Java/jre1.5.0_05/bin/client/jvm.dll
    @type jvm: string

    @param oobase: the base directory where we will
    find basis3.3/program/classes where we find the unoil.jar package
    @type oobase: string

    @param urebase: the base directory where we will find ure/share/java inside
    which we should find java_uno.jar, juh.jar, jurt.jar, unoloader.jar
    @type oobase: string

    @param office_version: the office version we want to use for rendering
    @type office_version: string

    @param max_mem: the maximum amount of mega bytes to allocate to
    our JVM
    @type max_mem: integer
    """

    context = get_oo_context(office_version)
    java_classpath_sep = context.get('java_classpath_sep')
    ure_subpath = context.get('ure_subpath')
    oooclasses_subpath = context.get('oooclasses_subpath')

    # this is our internally compiled java class
    jar = pkg_resources.resource_filename(
            'py3o.renderers.juno', 'py3oconverter.jar')
    oojars = list()

    for ureitem in ureitems:
        oojars.append(os.path.join(urebase, ure_subpath, ureitem))

    for basisitem in basisitems:
        oojars.append(os.path.join(oobase, oooclasses_subpath, basisitem))

    convertor_lib = os.path.abspath(jar)
    java_classpath = '-Djava.class.path=%s' % (convertor_lib)

    for oojar in oojars:
        java_classpath += "%s%s" % (java_classpath_sep, oojar)

    # -Xms is initial memory for java, -Xmx is maximum memory for java
    #java_initmem = "-Xms%sM" % max_mem
    java_maxmem = "-Xmx%sM" % max_mem
    jvm_abs = os.path.abspath(jvm)
    logging.debug('Starting JVM: %s with options: %s %s' % (
        jvm_abs, java_classpath, java_maxmem))
    startJVM(jvm_abs, java_classpath, java_maxmem)

class Convertor(object):

    def __init__(self, host, port):
        """init our java lib with the host and port for the open office server
        """
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()

        jconvertor_package = JPackage('py3oconverter').Convertor
        self.jconvertor = jconvertor_package(host, port)

    def convert(self, infilename, outfilename, filter):
        # use our java lib...
        self.jconvertor.convert(infilename, outfilename, filter)

