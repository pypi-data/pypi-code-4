import logging
import re
from clover import get_package_resource
from clover.closure.inputmanifest import InputManifest
from clover.config.baseconfig import interpret_path
from clover.sourcefiles.scan import scan_for_test_files, find_sourcefiles_from_inputs, find_sourcefiles_in_paths
from clover.config.dictconfig import DictConfig
from clover.config.options import Options

logger = logging.getLogger('clover.config.CloverConfig')

def get_added_removed(old, new):

    intersect = old.intersection(new)

    added = new - intersect
    removed =  old - intersect

    return (added, removed)

class CloverConfig(DictConfig):
    """ Clover specific config class.
    """
    options = Options

    _build_manifest = None

    def get_id(self):
        return self.read_option(self.options.id)

    def abspath(self, path):
        return interpret_path(path, self.basedir)


    def find_tests(self):
        testfiles = set()
        for path in self.read_option(self.options.paths):
            path = self.abspath(path)

            for file in scan_for_test_files(path):
                testfiles.add(file)
        return testfiles


    def get_build_manifest(self):
        """ Returns a build manifest. Refreshes if cached.
        """
        if self._build_manifest is None:
            required_sources = self.get_input_sourcefiles()
            all_sources = self.get_library_sourcefiles() | self.get_sourcefiles_in_paths()
            self._build_manifest = InputManifest(required_sources, all_sources)
        else:
            self.refresh_manifest(self._build_manifest)

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

        options.setClosurePass(True)

        if self.read_option(self.options.use_type_optimizations):
            level.setTypeBasedOptimizationOptions(options)
        

        # set the warning level
        warning_level_name = self.read_option(self.options.logging)
        warning_level = runtime.gateway.getNamedWarningLevel(warning_level_name)
        warning_level.setOptionsForWarningLevel(options)

        # path to a temp file
        options.setSourceMapOutputPath("sourcemap")
        #options.setManageClosureDependencies(True)

        translatations_file = self.read_option(self.options.translations)
        if translatations_file:
            logging.debug('Attaching translations.')
            translatations_file = self.abspath(translatations_file)
            message_bundle = runtime.gateway.newMessageBundle(open(translatations_file).read(), None)
            options.setMessageBundle(message_bundle)

        #options.setInstrumentForCoverage(True)
        options.setPrettyPrint(self.read_option(self.options.pretty_print))


        checks = self.read_option(self.options.checks)

        CHECKLEVELS = {
            'WARNING': runtime.gateway.getNamedCheckLevel('WARNING'),
            'ERROR': runtime.gateway.getNamedCheckLevel('ERROR'),
            'OFF': runtime.gateway.getNamedCheckLevel('OFF')
        }

        groups = runtime.gateway.getDiagnosticGroups()
        for checkName, checkLevelName in checks.items():

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
            options.setAliasAllStrings(self.read_option(self.options.alias_all_strings))
            options.setAliasExternals(self.read_option(self.options.alias_externals))
            options.setAliasKeywords(self.read_option(self.options.alias_keywords))
            options.setExportTestFunctions(self.read_option(self.options.export_test_functions))
            options.setAmbiguateProperties(self.read_option(self.options.ambiguate_properties))
            options.setDisambiguateProperties(self.read_option(self.options.disambiguate_properties))

            #options.setInstrumentForCoverage(True)
            options.setOutputCharset(self.read_option(self.options.charset))

            print_input_delimeter = self.read_option(self.options.print_input_delimeter)

            if print_input_delimeter:
                options.setPrintInputDelimter(True)
                options.setInputDelimeter("// Input %num%: %name%")

            # build sets for strip options
            name_prefixes = runtime.new_set(self.read_option(self.options.strip_name_prefixes))
            name_suffixes = runtime.new_set(self.read_option(self.options.strip_name_suffixes))
            type_prefixes = runtime.new_set(self.read_option(self.options.strip_type_prefixes))

            options.setStripNamePrefixes(name_prefixes)
            options.setStripNameSuffixes(name_suffixes)
            options.setStripTypePrefixes(type_prefixes)


            #options.setDefineToBooleanLiteral(name, primitive.getAsBoolean());
            #options.setDefineToStringLiteral(name, primitive.getAsString());
            #options.setDefineToNumberLiteral(name, primitive.getAsInt());
            #options.setDefineToDoubleLiteral(name, primitive.getAsDouble());

            # Generates goog.exportSymbol/goog.exportProperty for the @export annotation.
            options.setGenerateExports(True)


            # Controls the ExternExportsPass:
            # Creates an externs file containing all exported symbols and properties
            # for later consumption. 
            options.setExternExports(True)



    def refresh_manifest(self, manifest):
        logger.debug('Refreshing manifest.')

        all_sourcefiles = self.get_library_sourcefiles() | self.get_sourcefiles_in_paths()

        new_sourcefiles, removed_sourcefiles = get_added_removed(manifest.all_sourcefiles, all_sourcefiles)

        logger.debug('Adding sources %s', new_sourcefiles)
        logger.debug('Removed sources %s', removed_sourcefiles)

        # remove any that dont exist
        for sourcefile in manifest.all_sourcefiles:
            if not sourcefile.check_exists():
                logger.debug('Removed source %s', sourcefile)
                removed_sourcefiles.add(sourcefile)

        # add any new sourcefiles
        manifest.all_sourcefiles |= new_sourcefiles

        # remove any removed
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