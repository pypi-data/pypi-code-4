#!/usr/bin/python

""" Parses through the python source code to generate HTML documentation.  """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import datetime
import distutils.dir_util
import logging
import os.path
import shutil

from xml.etree import ElementTree

import projex
import projex.text
import projex.wikitext

from projex.enum import enum

from projex        import resources
from projex.docgen import templates
from projex.docgen import commands

logger = logging.getLogger(__name__)

#----------------------------------------------------------------------

class DoxSource(object):
    Type = enum('Wiki', 'Module', 'Group')
    
    def __init__(self, dox, typ, name, filepath):
        self._dox = dox
        self._type = typ
        self._name = name
        self._filepath = filepath
        self._sources = []
    
    def addSource(self, source):
        """
        Adds a new source to this source.  Sources can be grouped
        together to create custom hierarchies.
        
        :param      source | <DoxSource>
        """
        self._sources.append(source)
    
    def export(self, outpath, breadcrumbs=None):
        """
        Exports this source to the given output path location.
        
        :param      outpath | <str>
        """
        if breadcrumbs is None:
            breadcrumbs = ['Home']
        
        # generate an arbitrary group
        if self.type() == DoxSource.Type.Group:
            key = self.name().replace(' ', '_').lower()
            target = os.path.join(outpath, key)
            if not os.path.exists(target):
                os.mkdir(target)
            
            breadcrumbs.append(self.name())
            for source in self.sources():
                source.export(target, breadcrumbs)
        
        # generate user docs
        elif self.type() == DoxSource.Type.Wiki:
            first = True
            
            # generate wiki documentation
            for rootpath, folders, files in os.walk(self.filepath()):
                # initialize group options
                group = os.path.normpath(rootpath).split(os.path.sep)[-1]
                group = projex.text.pretty(group)
                
                if not first:
                    breadcrumbs.append(group)
                    outpath = os.path.join(outpath,
                                           projex.text.underscore(group))
                    
                    if not os.path.exists(outpath):
                        os.mkdir(outpath)
                
                # generate wiki files
                for filename in files:
                    if not filename.endswith('.wiki'):
                        continue
                    
                    # extract wiki information
                    filepath = os.path.join(rootpath, filename)
                    wiki_file = open(filepath, 'r')
                    wiki_contents = wiki_file.read()
                    wiki_file.close()
                    
                    # generate the contents
                    title = projex.text.pretty(filename.split('.')[0])
                    
                    # generate the breadcrumbs for this file
                    incl = filename != 'index.wiki'
                    html = self._dox.render(title,
                                            wiki_contents,
                                            breadcrumbs,
                                            filepath=filepath,
                                            includeTitleInCrumbs=incl)
                    
                    # generate the new html file
                    targetfile = filename.replace('.wiki', '.html')
                    target = os.path.join(outpath, targetfile)
        
                    html_file = open(target, 'w')
                    html_file.write(html)
                    html_file.close()
                
                first = False
        
        # generate module docs
        elif self.type() == DoxSource.Type.Module:
            pass
    
    def filepath(self):
        """
        Returns the filepath for the source of this source.
        
        :return     <str>
        """
        path = os.path.expandvars(self._filepath)
        if os.path.isabs(path):
            return path
        
        elif self._dox.filename():
            basepath = os.path.dirname(self._dox.filename())
            basepath = os.path.join(basepath, path)
        
        else:
            basepath = path
        
        return os.path.abspath(basepath)
    
    def name(self):
        """
        Returns the name for this source.
        
        :return     <str>
        """
        return self._name
    
    def sources(self):
        """
        Returns a list of the sub-sources this instance holds.  Sources
        can be nested together in groups to create custom hierarchies.
        
        :return     [<DoxSource>, ..]
        """
        return self._sources
    
    def toXml(self, xml):
        """
        Converts this source information to xml data.
        
        :param      xml | <ElementTree.Element>
        
        :return     <ElementTree.SubElement>
        """
        xsource = ElementTree.SubElement(xml, 'source')
        xsource.set('type', DoxSource.Type[self.type()])
        xsource.set('name', self.name())
        xsource.text = self._filepath
        
        for source in self.sources():
            source.toXml(xsource)
        
        return xsource
    
    def type(self):
        """
        Returns the type of source this source is.
        
        :return     <DoxSource.Type>
        """
        return self._type
    
    @staticmethod
    def fromXml(dox, xml):
        """
        Generates a new source based on the inputed xml node.
        
        :param      xml | <ElementTree.Element>
        
        :return     <DoxSource>
        """
        typ = DoxSource.Type[xml.get('type')]
        rsc = DoxSource(dox, typ, xml.get('name', ''), xml.text)
        
        # load sub-sources
        for xchild in xml:
            rsc.addSource(DoxSource.fromXml(dox, xchild))
        
        return rsc
        

#----------------------------------------------------------------------

class DoxFile(object):
    _current = None
    
    def __init__(self):
        self._filename = ''
        
        # configuration info
        self._config = {}
        self._config['company'] = 'Projex Software, LLC'
        self._config['companyUrl'] = 'http://www.projexsoftware.com/'
        self._config['theme'] = 'base'
        self._config['themePath'] = ''
        self._config['title'] = 'Dox Documentation'
        self._config['version'] = '0.0'
        self._config['copyright'] = ''
        self._config['resourcePath'] = ''
        
        # additional properties
        self._navigation = []
        self._sources = []
    
    def addNavigation(self, title, url):
        """
        Adds a navigation link to the main navigation menu bar for the
        documentation.
        
        :param      title | <str>
                    url   | <str>
        """
        self._navigation.append((title, url))
    
    def addSource(self, source):
        """
        Adds the inputed source to the list of sources for this instance.
        
        :param      source | <DoxSource>
        """
        self._sources.append(source)
    
    def config(self, key, default=None):
        """
        Returns the configuration value for the inputed key.
        
        :param      key | <str>
        """
        return self._config.get(key, default)
    
    def company(self):
        """
        Returns the company name for this dox file.
        
        :return     <str>
        """
        return self.config('company')
    
    def companyUrl(self):
        """
        Returns the company url for this dox file.
        
        :return     <str>
        """
        return self.config('companyUrl')
    
    def copyright(self):
        """
        Returns the copyright information for this dox file.
        
        :return     <str>
        """
        copyright = self.config('copyright')
        
        if not copyright:
            copyright = 'genreated by <a href="%s">docgen</a> '\
                        'copyright &copy; <a href="%s">%s</a> %s'
            
            opts = (projex.website(),
                    self.companyUrl(),
                    self.company(),
                    datetime.date.today().year)
            
            copyright %= opts
        
        return copyright
    
    def export(self, outpath):
        """
        Builds the files that will be used to generate the different help
        documentation from the dox sources within this configuration file.
        
        :param      outpath | <str>
        """
        self.initEnviron()
        
        #----------------------------------------------------------------------
        
        # clear the output location
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
        
        # create the output location
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        
        # generate the source files
        for source in self.sources():
            source.export(outpath)
        
        # copy the resources and syntax code
        static_path = os.path.join(outpath, '_static')
        paths = []
        paths.append(resources.find('ext/prettify'))
        paths.append(templates.path('javascript'))
        paths.append(templates.path('css'))
        paths.append(templates.path('images'))
        paths.append(templates.path('img'))
        
        # copy static resources
        for path in paths:
            if not os.path.exists(path):
                continue
            
            basename = os.path.basename(path)
            target   = os.path.join(static_path, basename)
            
            distutils.dir_util.copy_tree(path, target, update=1)
        
        # include dynamic resources
        for resource in self.resourcePaths():
            for subpath in os.listdir(resource):
                filepath = os.path.join(resource, subpath)
                outpath = os.path.join(static_path, subpath)
                
                if os.path.isdir(filepath):
                    distutils.dir_util.copy_tree(filepath, outpath, update=1)
                else:
                    shutil.copyfile(filepath, outpath)
        
        return True
    
    def filename(self):
        """
        Returns the filename associated with this dox file.
        
        :return     <str>
        """
        return self._filename
    
    def initEnviron(self):
        """
        Initializes the docgen build environment settings with this
        dox file's configuration information.
        """
        # setup the templating
        templates.setTheme(self.theme())
        templates.setThemePath(self.themePath())
        
        # initialize navigation
        templ = templates.template('link_navigation.html')
        nav = []
        for title, url in self.navigation():
            nav.append(templ % {'title': title, 'url': url})
        
        # set the environment variables
        commands.ENVIRON.clear()
        commands.ENVIRON['module_title'] = self.title()
        commands.ENVIRON['module_version'] = self.version()
        commands.ENVIRON['copyright'] = self.copyright()
        commands.ENVIRON['navigation'] = ''.join(nav)
    
    def navigation(self):
        """
        Returns the navigation links for this dox file.
        
        :return     [(<str> title, <str> url), ..]
        """
        return self._navigation
    
    def render(self,
               title,
               contents,
               breadcrumbs=None,
               baseUrl=None,
               staticUrl=None,
               filepath='',
               includeTitleInCrumbs=False):
        """
        Renders the inputed text to HTML for this dox, including the
        inputed breadcrumbs when desired.
        
        :param      title | <str>
                    contents | <DoxSource.Type>
                    breadcrumbs | [<str>, ..] || None
        
        :return     <str>
        """
        curdir = os.curdir
        if self.filename():
            os.chdir(os.path.dirname(self.filename()))
        
        if breadcrumbs is None:
            breadcrumbs = ['Home']
        
        count = len(breadcrumbs) - 1
        if baseUrl is None:
            baseUrl = '.' + '/..' * count
        
        if staticUrl is None:
            staticUrl = baseUrl + '/_static'
        
        page_templ  = templates.template('page.html')
        crumb_templ = templates.template('link_breadcrumbs.html')
        nav_templ   = templates.template('link_navigation.html')
        
        # extract the mako template information
        templatePaths = self.templatePaths()
        
        options = {}
        options['__file__'] = filepath
        contents = projex.wikitext.render(contents,
                                          commands.url_handler,
                                          options=options,
                                          templatePaths=templatePaths)
        
        # generate the breadcrumb links
        crumbs = []
        for i, crumb in enumerate(breadcrumbs):
            url = '.' + '/..' * (count - i) + '/index.html'
            opts = {'text': crumb, 'url': url}
            crumbs.append(crumb_templ % opts)
        
        if includeTitleInCrumbs:
            crumbs.append(crumb_templ % {'text': title, 'url': ''})
        
        # generate the environ data
        environ = {}
        environ['base_url']       = baseUrl
        environ['static_url']     = staticUrl
        environ['title']          = title
        environ['contents']       = contents
        environ['breadcrumbs']    = ''.join(crumbs)
        environ['module_title']   = self.title()
        environ['module_version'] = self.version()
        environ['copyright']      = self.copyright()
        
        # create navigation links
        nav = []
        for title, url in self.navigation():
            href = url % environ
            nav.append(nav_templ % {'title': title, 'url': href})
        
        environ['navigation'] = ''.join(nav)
        
        os.chdir(curdir)
        
        # generate the html
        return page_templ % environ
    
    def resourcePath(self):
        """
        Returns the path to the resources for this doxfile
        
        :return     <str>
        """
        return self.config('resourcePath', '')
    
    def resourcePaths(self):
        """
        Returns a list of the resource paths for this doxfile.
        
        :return     <str>
        """
        resource_path = self.resourcePath()
        if not resource_path:
            return []
        
        output   = []
        basepath = os.path.dirname(self.filename())
        for path in resource_path.split(os.path.pathsep):
            path = os.path.expandvars(path)
            if os.path.isabs(path):
                output.append(path)
            else:
                path = os.path.abspath(os.path.join(basepath, path))
                output.append(path)
        
        return output
    
    def save(self):
        """
        Saves the doxfile to the current filename.
        
        :return     <bool> | success
        """
        return self.saveAs(self.filename())
    
    def saveAs(self, filename):
        """
        Saves this doxfile out to a file in XML format.
        
        :param      filename | <str>
        
        :return     <bool> | success
        """
        if not filename:
            return False
        
        elem = self.toXml()
        projex.text.xmlindent(elem)
        
        content = ElementTree.tostring(elem)
        
        try:
            f = open(filename, 'w')
            f.write(content)
            f.close()
        except IOError:
            logger.exception('Could not save DoxFile')
            return False
        return True
    
    def setCompany(self, company):
        """
        Sets the company for this dox file.
        
        :param      company | <str>
        """
        self.setConfig('company', company)
    
    def setCompanyUrl(self, url):
        """
        Sets the company url this dox file.
        
        :param      company | <str>
        """
        self.setConfig('companyUrl', url)
    
    def setCopyright(self, copyright):
        """
        Sets the copyright values for this dox file to the inputed value.
        
        :param      copyright | <str>
        """
        self.setConfig('copyright', copyright)
    
    def setConfig(self, key, value):
        """
        Sets the configuration value for this dox file to the inputed data.
        
        :param      key | <str>
                    value | <str>
        """
        self._config[key] = value
    
    def setFilename(self, filename):
        """
        Sets the filename for this dox file to the inputed file.
        
        :param      filename | <str>
        """
        self._filename = str(filename)
    
    def setNavigation(self, navigation):
        """
        Sets the navigation to the inputed list of navigation urls and titles.
        
        :param      navigation | [(<str> title, <str> url), ..]
        """
        self._navigation = navigation
    
    def setResourcePath(self, path):
        """
        Sets the resource path for this dox file to the inputed path.
        
        :param      path | <str>
        """
        self.setConfig('resourcePath', path)
    
    def setResourcePaths(self, paths):
        """
        Sets the resource path information for this dox file to the inputed
        list of files.
        
        :param      paths | [<str>, ..]
        """
        self.setResourcePath(os.path.pathsep.join(map(str, paths)))
    
    def setTemplatePath(self, path):
        """
        Sets the template path for this doxfile to the inputed path.
        
        :param      path | <str>
        """
        self.setConfig('templatePath', path)
    
    def setTemplatePaths(self, paths):
        """
        Sets the string of template paths for this dox file to the inputed
        list of paths.  This list will be used when rendering mako files
        to have as templatable options.
        
        :param      paths | <str>
        """
        self.setTemplatePath(os.path.pathsep.join(map(str, paths)))
    
    def setTheme(self, theme):
        """
        Sets the theme that will be used for this dox file.
        
        :param      theme | <str>
        """
        self.setConfig('theme', theme)
    
    def setThemePath(self, themePath):
        """
        Sets the theme path that will be used when loading the theme of
        this dox file.  If a blank string is specified, then the default theme
        locations will be used.
        
        :param      themePath | <str>
        """
        self.setConfig('themePath', themePath)
    
    def setTitle(self, title):
        """
        Sets the title for this dox file to the inputed title.
        
        :param      title | <str>
        """
        self.setConfig('title', title)
    
    def setVersion(self, version):
        """
        Sets the vesion for this dox file to the inputed version.
        
        :param      version | <str>
        """
        self.setConfig('version', version)
    
    def sources(self):
        """
        Returns a list of the sources for this dox file.
        
        :return     [<DoxSource>, ..]
        """
        return self._sources
    
    def templatePath(self):
        """
        Returns the template path linked with this dox file.
        
        :return     <str>
        """
        return self.config('templatePath', '')
    
    def templatePaths(self):
        """
        Returns a string with path separated template path locations for
        additional mako templates.
        
        :return     <str>
        """
        template_path = self.templatePath()
        if not template_path:
            return []
        
        output   = []
        basepath = os.path.dirname(self.filename())
        for path in template_path.split(os.path.pathsep):
            path = os.path.expandvars(path)
            if os.path.isabs(path):
                output.append(path)
            else:
                path = os.path.abspath(os.path.join(basepath, path))
                output.append(path)
        return output
    
    def theme(self):
        """
        Returns the theme for this dox file.
        
        :return     <str>
        """
        return self.config('theme')
    
    def themePath(self):
        """
        Returns the theme path for this dox file.
        
        :return     <str>
        """
        path = self.config('themePath')
        if not path:
            return resources.find('docgen/%s/' % self.theme())
        return path
    
    def toXml(self):
        """
        Converts this dox file to XML.
        
        :return     <ElementTree.Element>
        """
        xml = ElementTree.Element('dox')
        xml.set('version', '1.0')
        
        # store the configuration data
        xconfig = ElementTree.SubElement(xml, 'config')
        
        for key, value in self._config.items():
            xattr = ElementTree.SubElement(xconfig, key)
            xattr.text = value
        
        # store the navigation data
        xnavigation = ElementTree.SubElement(xml, 'navigation')
        for title, url in self.navigation():
            xlink = ElementTree.SubElement(xnavigation, 'link')
            xlink.set('title', title)
            xlink.text = url
        
        # store source data
        for source in self.sources():
            source.toXml(xml)
    
    def title(self):
        """
        Returns the title for this dox file.
        
        :return     <str>
        """
        return self.config('title')
    
    def version(self):
        """
        Returns the version for this dox file.
        
        :return     <str>
        """
        return self.config('version')
    
    @staticmethod
    def current():
        """
        Returns the current instance of this dox file.
        
        :return     <DoxFile> || None
        """
        return DoxFile._current
    
    @staticmethod
    def load(filename):
        """
        Loads the dox file from the inputed filename.
        
        :param      filename | <str>
        
        :return     <DoxFile>
        """
        try:
            xml = ElementTree.parse(filename)
        except:
            return DoxFile()
        
        dox = DoxFile()
        dox.setFilename(filename)
        
        # update configuration information
        xconfig = xml.find('config')
        if xconfig is not None:
            for xattr in xconfig:
                dox.setConfig(xattr.tag, xattr.text)
        
        # update navigation information
        xnavigation = xml.find('navigation')
        if xnavigation is not None:
            for xlink in xnavigation:
                dox.addNavigation(xlink.get('title'), xlink.text)
        
        # load source information
        xsources = xml.find('sources')
        if xsources is not None:
            for xsource in xsources:
                dox.addSource(DoxSource.fromXml(dox, xsource))
        
        return dox
    
    @staticmethod
    def setCurrent(doxfile):
        """
        Returns the current instance of this dox file.
        
        :param      doxfile | <DoxFile> || None
        """
        DoxFile._current = doxfile
    