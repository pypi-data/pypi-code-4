from __future__ import absolute_import
import os

class Option(object):
    required = False
    name = None
    
    def __init__(self):
        pass
    
    @classmethod
    def get_name(cls):
        return cls.name
    
    @classmethod
    def get_required(cls):
        return cls.required
    
    @classmethod
    def has_default(cls):
        return hasattr(cls, 'default')
    
    def get_default(self, config):
        if hasattr(self.default, '__call__'):
            return self.default(config)
        
        return self.default
        
    def validate(self):
        pass

class Validator(object):
    def validate(self, config, value):
        raise NotImplementedError

class String(Validator):
    def validate(self, config, value):
        assert isinstance(value, basestring), "Must be a string."
        return value
        
class Strings(Validator):
    def validate(self, config, value):
        assert isinstance(value, list), "Must be a list of strings."
        return value

class Boolean(Validator):
    def validate(self, config, value):
        assert isinstance(value, bool),  "Must be a boolean."
        return value
        
        
def interpret_path(path, basedir):
    if not path.startswith('/'):
        return os.path.abspath(os.path.normpath(os.path.join(basedir, path)))
    else:
        return os.path.abspath(os.path.expanduser(path))
    
class Path(Validator):
    def validate(self, config, value):
        assert isinstance(value, basestring), "Path must be a string."
        path = interpret_path(value, config.basedir)
        
        if not os.path.exists(path):
            raise AssertionError("Path does not exist: %s" % path)
        return path
    
class Paths(Validator):
    def validate(self, config, value):
        assert isinstance(value, list), "Must be a list of paths."
        absolute_paths = []
        for path in value:
            path = interpret_path(path, config.basedir)
            if not os.path.exists(path):
                raise AssertionError("Path does not exist: %s" % path)
            absolute_paths.append(path)
            
        return absolute_paths 

class Options(object):
    
    class ambiguate_properties(Option):
        """ Rename unrelated properties to the same name to reduce code size.
        """
        name = 'ambiguate-properties'
        validator = Boolean()
        default = False
        
    class alias_all_strings(Option):
        """ Aliases all string literals to global instances, to avoid creating more objects than              necessary.
        """
        name = 'alias-all-strings'
        validator = Boolean()
        default = False
    
    class alias_keywords(Option):
        """ Aliases true, false, and null to variables with shorter names.
        """
        name = 'alias-keywords'
        validator = Boolean()
        default = False
        
    class alias_externals(Option):
        """ Adds variable aliases for externals to reduce code size.
        """
        name = 'alias-externals'
        validator = Boolean()
        default = False
        
        
    class charset(Option):
        """ Output character set.
            Default: UTF-8.
        """
        class Validator(Validator):
            def validate(self, config, value):
                return value
        name = 'charset' 
        validator = Validator()
        default = 'UTF-8'
    
    
    class default_externs(Option):
        """ Whether the default externs should be used by the compiler.
        """
        name = 'default-externs'
        validator = Boolean()
        default = True
        
    class define(Option):
        """ An object literal that contains a mapping of variables in the JavaScript code that are annotated with 
        @define (indicating that they can be redefined at compile time) to the values that should be substituted. The
         following should be specified to set goog.DEBUG to false at compile time:
            
                define:
                  goog.DEBUG: false
                  
            Note that these compile-time defines will only take effect when the code is compiled in either SIMPLE or 
            ADVANCED modes.
        """
        class Validator(Validator):
            def validate(self, config, value):
                return value        
            
        name = 'define'
        validator = Validator()
        
    
        
    class disambiguate_properties(Option):
        name = 'disambiguate-properties'
        validator = Boolean()
        default = True
        
    class checks(Option):
        class Validator(Validator):
            def validate(self, config, value):
                #assert value in ['ERROR', 'OFF', 'WARNING']
                return value
            
        name = 'checks'
        validator = Validator()
        default = {}
        
    class closure_library(Option):
        """ True to enable closure library inclusion.
        """
        name = 'closure-library'
        validator = Path()
        default = False
    
    
    class closure_library_disable(Option):
        """ Whether to include
        """
        name = 'disable-closure-library'
        validator = Boolean()
        default = False
        
    class debug(Option):
        """ Equivalent to the command-line --debug flag for the Closure Compiler. Defaults to false.
        """
        name = 'debug'
        validator = Paths()
        default = False
    
    class id(Option):
        """ Every config must have an id. 
        
            The id must be unique among the configs being served by clover because the id is a parameter to every 
            function in the clover REST API.
        """
        name = 'id'
        validator = String()
        required = True
        
    class inherits(Option):
        """ Every config must have an id. 
        
            The id must be unique among the configs being served by clover because the id is a parameter to every 
            function in the clover REST API.
        """
        name = 'inherits'
        validator = String()

        
    class export_test_functions(Option):
        """ When compiled, all global functions that start with test will be exported via goog.exportSymbol() so that
         when run as part of the Closure testing framework, the test methods will still be able to be discovered. In 
         short, this makes it possible to unit test JavaScript code compiled in Advanced mode.
        """
        name = 'export-test-functions'
        validator = Boolean()
        default = False
    
    
    
    class externs(Option):
        """ Files that contain externs that should be included in the compilation. 
        
            By default, these will be used in addition to the default externs bundled with the Closure Compiler.

            There are also externs for third party libraries, such as jQuery and Google Maps, that are bundled with 
            the Closure Compiler but are not enabled by default.
            
            These additional extern files can be seen in the Closure Compiler's contrib/externs directory. Such 
            externs can be included with a // prefix as follows::
            
                externs:
                - //jquery-1.5.js
                - //google_maps_api_v3.js
                - //chrome_extensions.js
        """
        class Validator(Validator):
            message = "Must be a list of valid externs/paths."
            
            def validate(self, config, value):
                assert isinstance(value, list)
                return value
            
        name = 'externs'
        validator = Validator()
        
        
    class inputs(Option):
        """ Input files to be compiled.
        
            Each input file and its transitive dependencies will be included in the compiled output.
        """
        name = 'inputs'
        validator = Paths()
        required = True



    class mode(Option):   
        """ Compilation level, which must be one of "RAW", "WHITESPACE", "SIMPLE", or "ADVANCED". 
        
            The default value is "RAW".
        """
        class Validator(Validator):
            message = "Must be a compilation level."
            def validate(self, config, value):
                assert isinstance(value, basestring)
                assert value in ['ADVANCED', 'RAW', 'SIMPLE', 'WHITESPACE']
                return value
            
        name = 'mode'
        validator = Validator()
        default = 'RAW'
        
    class logging(Option):
        """ Logging output mode, which must be one of "QUIET", "DEFAULT", or "VERBOSE". 
        
            The default value is "DEFAULT".
        """
        class Validator(Validator):
            def validate(self, config, value):
                #"QUIET", 'DEFAULT', 'VERBOSE'
                return value
            
        name = 'logging'
        validator = Validator()
        default = 'QUIET'
    
    class output(Option):
        """ If specified, when the build command is used, clover will write the compiled output to this file rather 
        than standard out.
        """
        name = 'output-file'
        validator = Path()
    
    class output_sourcemap(Option):
        """ If specified, when the build command is used, clover will write the compiled output to this file rather 
        than standard out.
        """
        name = 'output-sourcemap'
        validator = Path()
    
    class output_wrapper(Option):
        """ If specified, a template into which compiled JavaScript will be written. The placeholder for compiled 
        code is %output%, so to wrap the compiled output in an anonymous function preceded by a copyright comment, 
        specify:

                output-wrapper: |
                    // Copyright 2011
                    (function(){%output%})();
                
            The value may also be an array of strings that will be concatenated together:
            
                output-wrapper:
                  - var http = require('http');
                  - var https = require('https');
                  - var nodeUrl = require('url');
                  
            This is helpful if there are many lines to include that would normally be hard to read if the template 
            were one long string.
            
        """
        name = 'output-wrapper'
        validator = String()
    
    
    class paths(Option):
        """ Files or directories where the transitive dependencies of the inputs can be found.
        """
        name = 'paths'
        validator = Paths()
        default = []
    
    class pretty_print(Option):
        """ Equivalent to the command-line --formatting=PRETTY_PRINT flag for the Closure Compiler. Defaults to false.
        """
        name = 'pretty-print'
        validator = Boolean()
        default = False
        
        
    class print_input_delimeter(Option):
        """ Equivalent to the command-line --formatting=PRINT_INPUT_DELIMITER flag 
            for the Closure Compiler. Defaults to false.
        """
        name = 'print-input-delimeter'
        validator = Boolean()
        default = False
        
    
    class strip_name_suffixes(Option):
        """ Name suffixes that determine which variables and properties to strip.
         
            This can be useful for removing loggers::
                    
                strip-name-suffixes:
                - logger_
                
        """
        name = 'strip-name-suffixes'
        validator = Strings()
        default = []
        
    class strip_name_prefixes(Option):
        """ Qualified type name prefixes that determine which types to strip.
        """
        name = 'strip-name-prefixes'
        validator = Strings()
        default = []
        
        
    class strip_type_prefixes(Option):
        """ Qualified type name prefixes that determine which types to strip.
        """
        name = 'strip-type-prefixes'
        validator = Strings()
        default = []
    
    
    class test_excludes(Option):
        """ By default, all files that end in _test.js under the paths directories are included in the test runner 
        that runs all of the JS unit tests. This option can be used to specify subpaths of paths that should be 
        excluded from testing.

            For example, if the closure-library option is used to specify a custom Closure Library, 
            then it is likely that third_party/closure will be specified as a path to include utilities such as goog
            .async.Deferred. Including such a directory will also include closure/goog/dojo/dom/query_test.js, 
            which fails when run by clover because its corresponding query_test.html file includes a hardcoded path to
             base.js that cannot be loaded by clover. If this is a problem, then third_party/closure should be 
             included as an argument to test-excludes.
            
            See the section on testing for more details.
        """
        name = 'test-excludes'
        validator = Strings()    
       
       
    class translations(Option):
        """ An xtb translations file.
        """
        name = 'translations'
        validator = Path()

    class use_type_optimizations(Option):
        """ Enable additional optimizations that use type information.
        """
        name = 'use-type-optimizations'
        validator = Boolean()
        default = False


    class warnings(Option):
        """ Sets how warnings are treated.
        
            When set to true, warnings will be reported as errors.
        """
        name = 'warnings-error'
        validator = Boolean()
        default = False
        
    