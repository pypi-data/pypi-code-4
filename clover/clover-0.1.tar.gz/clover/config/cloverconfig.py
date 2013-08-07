import logging
import re
from clover import get_package_resource
from clover.closure.inputmanifest import InputManifest
from clover.config.baseconfig import interpret_path
from clover.sourcefiles.scan import scan_for_test_files, find_sourcefiles_from_inputs, find_sourcefiles_in_paths
from clover.config.dictconfig import DictConfig
from clover.config.options import Options

logger = logging.getLogger('clover.config.CloverConfig')

class CloverConfig(DictConfig):
    """ Clover specific config class.
    """
    options = Options
    
    def get_id(self):
        return self.read_option(self.options.id)

    def abspath(self, path):
        return interpret_path(path, self.basedir)


    def find_tests(self):
        testfiles = set()
        for path in self.read_option(self.options.paths):
            path = self.abspath(path)
        
            for file in scan_for_test_files(path):
                #testfiles.add(relative_path(file, config.basedir))
                testfiles.add(file)
        return testfiles
        
    _build_manifest = None
    
    def get_build_manifest(self):
        """ Returns and refreshes a build manifest. 
        """
        if self._build_manifest is None:
            required_sources = self.get_input_sourcefiles()
            all_sources = self.get_library_sourcefiles() | self.get_sourcefiles_in_paths()
            self._build_manifest = InputManifest(required_sources, all_sources)
        else:
            if self._build_manifest.have_sourcefiles_expired():
                logger.debug('Source files have expired. Refreshing manifest.')
                self.refresh_manifest()
        return self._build_manifest
    
    def apply_compiler_options(self, options, runtime):
        
        level_name = self.read_option(self.options.mode)
        level = runtime.gateway.getNamedCompilationLevel(level_name)
        logger.debug('Compiling at level: %s', level_name)
        
        # copy in the options for the given compilation level
        level.setOptionsForCompilationLevel(options)

        # handle debug modes
        if self.read_option(self.options.debug):
            logging.debug('Enabling debug mode. %s')
            level.setDebugOptionsForCompilationLevel(options)

        options.setCodingConvention(runtime.gateway.jvm.com.google.javascript.jscomp.ClosureCodingConvention())
        
        # set the warning level
        warning_level_name = self.read_option(self.options.logging)
        warning_level = runtime.gateway.getNamedWarningLevel(warning_level_name)
        warning_level.setOptionsForWarningLevel(options)
        
        # path to a temp file
        options.setSourceMapOutputPath("sourcemap")
        #options.setManageClosureDependencies(True)
        
        
        logging.debug('Attaching translations.')
        translatations_file = self.read_option(self.options.translations)
        if translatations_file:
            translatations_file= self.abspath(translatations_file)
            message_bundle = runtime.gateway.newMessageBundle(open(translatations_file).read(),  None)
            options.setMessageBundle(message_bundle)
            
        #options.setInstrumentForCoverage(True)
        options.setPrettyPrint(self.read_option(self.options.pretty_print)) 
        
        
        #groups = runtime.gateway.getDiagnosticGroups()
        
        checks = self.read_option(self.options.checks)
        
        
        CHECKLEVELS = {
            'WARNING': runtime.gateway.getNamedCheckLevel('WARNING'),
            'ERROR': runtime.gateway.getNamedCheckLevel('ERROR'),
            'OFF': runtime.gateway.getNamedCheckLevel('OFF')
            
        }
        
        HYPHENS = re.compile('-([a-z])')
        
        def camelcaser(match):
            string = match.group(1)
            return string[:1].upper() + string[1:]
        
        groups = runtime.gateway.getDiagnosticGroups()
        for checkName, checkLevelName in checks.items():
            
            #checkName = HYPHENS.sub(camelcaser, checkName)
            group = groups.forName(checkName)
            
            if group is None:
                logger.warning('Unrecognized check %s', checkName)
                continue
            
            if checkLevelName is False:
                checkLevelName = 'OFF'
            
            options.setWarningLevel(group, CHECKLEVELS.get(checkLevelName))
            logging.debug('Setting checklevel %s: %s', checkName, checkLevelName)
        
        
        
        if True:
            # handle simple booleans
            options.aliasAllStrings = self.read_option(self.options.alias_all_strings) 
            options.exportTestFunctions = self.read_option(self.options.export_test_functions)
            options.ambiguateProperties = self.read_option(self.options.ambiguate_properties)
            options.disambiguateProperties = self.read_option(self.options.disambiguate_properties)
            
    
            #options.setInstrumentForCoverage(True)
            options.outputCharset = self.read_option(self.options.charset)
            
            print_input_delimeter = self.read_option(self.options.print_input_delimeter)
            
            if print_input_delimeter:
                options.printInputDelimeter = True
                options.inputDelimeter = "// Input %num%: %name%"
            
    
            logging.debug('Building strip sets.')
            name_suffixes = runtime.new_set(self.read_option(self.options.strip_name_suffixes))
            type_prefixes = runtime.new_set( self.read_option(self.options.strip_type_prefixes))
    
    
            options.stripNameSuffixes = name_suffixes
            options.stripTypePrefixes = type_prefixes
        
        
            #options.setDefineToBooleanLiteral(name, primitive.getAsBoolean());
            #options.setDefineToStringLiteral(name, primitive.getAsString());
            #options.setDefineToNumberLiteral(name, primitive.getAsInt());
            #options.setDefineToDoubleLiteral(name, primitive.getAsDouble());
            
    
            #
            options.generateExports = True
            
            
            
            # ?
            options.setExternExports(True)
        
        
    def refresh_manifest(self):
        
        manifest = self._build_manifest
        all_sourcefiles = self.get_library_sourcefiles() | self.get_sourcefiles_in_paths()
        all_manifest_sourcefiles = manifest.get_all_sourcefiles()
        
        new_sourcefiles = set()
        
        # add any new
        for sourcefile in all_sourcefiles:
            if sourcefile not in manifest.all_sourcefiles:
                logger.debug('Added source %s', sourcefile)
                new_sourcefiles.add(sourcefile)
                
        manifest.all_sourcefiles |= new_sourcefiles
                
                
        removed_sourcefiles = set()
        
        # remove any that dont exist
        for sourcefile in manifest.all_sourcefiles:
            if sourcefile not in all_manifest_sourcefiles:
                logger.debug('Removed source %s', sourcefile)
                removed_sourcefiles.add(sourcefile)
        
        manifest.all_sourcefiles = manifest.all_sourcefiles - removed_sourcefiles
    
        
    def get_input_sourcefiles(self):
        """ Find all source files specified by the inputs option. 
        """
        inputs = self.read_option(self.options.inputs)
        absolute_inputs = [interpret_path(path, self.basedir) for path in inputs]
        return find_sourcefiles_from_inputs(absolute_inputs)
    
    
    def get_sourcefiles_in_paths(self):
        """ Find all SourceFiles in the paths specified by the paths option. 
        """
        paths = [interpret_path(path, self.basedir) for path in self.read_option(self.options.paths)]
        return find_sourcefiles_in_paths(paths)
        
        
    def get_library_sourcefiles(self):
        """ Return a list of SourceFile for the closure library. 
        """
        
        closure_library = self.read_option(self.options.closure_library)

        library_paths = []

        if not closure_library:
            closure_library = get_package_resource('javascript/goog')
            # add soy (not in closure-library)
            soy_library = get_package_resource('javascript/soy')
            library_paths.append(soy_library)

        library_paths.append(closure_library)
        return find_sourcefiles_in_paths(library_paths)
    
    
    
#"checks": {
#  // Unfortunately, the Closure Library violates these in many places.
#  // "accessControls": "ERROR",
#  // "visibility": "ERROR"
#
#  "checkRegExp": "ERROR",
#  "checkTypes": "ERROR",
#  "checkVars": "ERROR",
#  "deprecated": "ERROR",
#  "fileoverviewTags": "ERROR",
#  "invalidCasts": "ERROR",
#  "missingProperties": "ERROR",
#  "nonStandardJsDocs": "ERROR",
#  "undefinedVars": "ERROR"
#}
#
#
#
#aggressiveVarCheck 
#
#
#brokenClosureRequiresLevel 
#checkGlobalNamesLevel
#checkGlobalThisLevel 
#
#
#
#
#checkMissingGetCssNameLevel 
#checkMissingReturn 
#
#checkProvides 
#           
#checkRequires 
#checkUnreachableCode 




#reportMissingOverride