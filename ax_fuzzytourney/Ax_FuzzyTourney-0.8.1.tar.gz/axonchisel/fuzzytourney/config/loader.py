"""
Ax_FuzzyTourney - configuration loading library.

This module may be used to load Tournaments from various file formats
including JSON and YAML.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import json
import StringIO

try:
    import yaml
except ImportError as e:
    # PyYAML not installed, but still allow execution without YAML support
    pass

import axonchisel.fuzzytourney.error as error
import axonchisel.fuzzytourney.config.component as component
import axonchisel.fuzzytourney.input as input_formats
import axonchisel.fuzzytourney.select as select_functions
import axonchisel.fuzzytourney.output as output_formats
import axonchisel.fuzzytourney.field as outfield_functions
import axonchisel.fuzzytourney.lens as lens_functions
import axonchisel.fuzzytourney.map as map_functions
import axonchisel.fuzzytourney.reduce as reduce_functions


# ----------------------------------------------------------------------------


class Loader:
    """Superclass for config loaders."""

    def _load_class(self, dottedpath, what):
        """Load class by full dotted name, for purpose 'what'."""
        splitpath = dottedpath.split('.')
        modulename = '.'.join(splitpath[:-1])
        classname = splitpath[-1]
        try:
            module = __import__(modulename, globals(), locals(), [classname])
        except ImportError:
            raise error.ConfigValueError(u"Unable to import {0} module '{1}'".format(what, dottedpath))
        try:
            return getattr(module, classname)
        except AttributeError:
            raise error.ConfigValueError(u"Unable to find {0} class '{1}' loading '{2}'".format(what, classname, dottedpath))
        

# ----------------------------------------------------------------------------

    
class Loader_JSON(Loader):
    """Loads config from JSON file-like object."""
    
    def __init__(self):
        self._f = None
        self._json = None
        self._tournament = None
        self._app_context = None   # opaque obj for app to pass data to dynamic functions
    
    def set_file(self, f):
        """Set file-like object to load from."""
        self._f = f
    
    def set_app_context(self, app_context):
        """
        Set new app context opaque obj, for communicating between app and internals.
        Useful for e.g. config information used by custom function extensions.
        """
        self._app_context = app_context
        
    def load_tournament(self):
        """Load, parse, verify, and return Tournament object."""
        try:
            loaded_json = json.load(self._f)
        except ValueError as e:
            raise error.ConfigSyntaxError("Invalid JSON detected: {0!r}".format(e))
        self._json = self._must_get(loaded_json, 'tournament')
            
        self._tournament = component.Tournament()
        self._parse_tournament()
        
        return self._tournament
    
    def _parse_tournament(self):
        """Main parse function."""
        self._tournament = component.Tournament()
        self._parse_tournament_metadata()
        self._parse_input()
        self._parse_select()
        self._parse_output()
        self._parse_criteria()
        self._parse_judges()

    def _parse_tournament_metadata(self):
        """
        Parse tournament top level metadata.
        Example:
            "name": "...",
            "desc": "..."
        """
        self._tournament.name = self._json.get('name', "")
        self._tournament.desc = self._json.get('desc', "")

    def _parse_input(self):
        """
        Parse input section from JSON.
        Example:
            "input": {
                "fn": "text_lines_int",
                "config": { "src": "/path/to/input.txt" }
            },
        """
        jinput = self._must_get(self._json, 'input')
        self._parse_function(self._tournament.input, jinput, 
            input_formats, 'InputFormat', "input format")

    def _parse_output(self):
        """
        Parse output section from JSON.
        Example:
            "output": {
                "fn": "text_csv",
                "config": { "csv_header": "names", "dest": "results.csv" },
                "fields": [
                    "progress",
                    "entrant_num",
                    {"fn": "entrant", "config": {"id": "input_val", "name": "Input Val"}},
                    {"fn": "criterion", "config": {"criterion": "score_risk_cancel"}},
                    {"fn": "rand", "config": {"count": 3}}
                ],
            },
        """
        joutput = self._must_get(self._json, 'output')
        self._parse_function(self._tournament.output, joutput, 
            output_formats, 'OutputFormat', "output format")

        jfields = self._must_get(joutput, 'fields')
        self._tournament.output.fields = self._parse_output_fields(jfields)

    def _parse_output_fields(self, jfields):
        """Parse output fields section from JSON."""
        fields = []
        for jfield in jfields:
            field = component.OutputField()
            self._parse_function(field, jfield, 
                outfield_functions, 'OutputFieldFunction', "output field function")
            fields.append(field)
        return fields

    def _parse_select(self):
        """
        Parse select section from JSON.
        Example:
            "select": {
                "fn": "top_n_criteria",
                "config": { "n": 2, "sort": "desc", "criterion": "score_risk_cancel" }
            },
        """
        jselect = self._must_get(self._json, 'select')
        self._parse_function(self._tournament.select, jselect, 
            select_functions, 'SelectFunction', "select format")

    def _parse_criteria(self):
        """
        Parse criteria section from JSON.
        Example:
            "criteria": [
                {
                    "id": "score_risk_cancel", "name": "Cancel Risk Factor", 
                    "init": 0.0,
                    "desc": "Calculation (0-100) of risk of customer loss"
                }
            ],
        """
        jcriteria = self._must_get(self._json, 'criteria')
        for jcriterion in jcriteria:
            criterion = component.Criterion()
            criterion.id = self._must_get(jcriterion, 'id')
            criterion.name = self._must_get(jcriterion, 'name')
            criterion.init = self._must_get(jcriterion, 'init')
            criterion.desc = self._must_get(jcriterion, 'desc')
            self._tournament.criteria.criteria.append(criterion)
        
    def _parse_judges(self):
        """
        Parse judges section from JSON.
        Example:
            "judges": [ {}, {}, ... ]
        """
        jjudges = self._must_get(self._json, 'judges')
        for jjudge in jjudges:
            judge = self._parse_judge(jjudge)
            self._tournament.judges.judges.append(judge)

    def _parse_judge(self, jjudge):
        """
        Parse judges section from JSON.
        Example:
            {
                "name": "Random judge",
                "desc": "Judges by random values",
                "heuristics": [
                    {
                        "lens": { "fn": "Random", "config": { "count": 3 } },
                        "maps": [
                            { "fn": "ClipWeight", "config": {
                                "range": [-1.0, null],
                                "score": {
                                    "in": { "base": 0, "weight": -100.0 },
                                    "out": { "below": 0.0, "above": 0.0 },
                                    "none": 0.0
                                }
                            }}
                        ],
                        "reduce": { "fn": "Mean", "config": {} },
                        "reduced_maps": [ { "fn": "Scale", "config": { "factor": 10 } } ],
                        "criterion": "score_risk_cancel",
                    }
                ]
            }
        """
        judge = component.Judge()
        judge.name = self._must_get(jjudge, 'name')
        judge.desc = self._must_get(jjudge, 'desc')
        jheuristics = self._must_get(jjudge, 'heuristics')
        heuristics = self._parse_heuristics(jheuristics)
        judge.heuristics += heuristics
        return judge

    def _parse_heuristics(self, jheuristics):
        """Parse heuristics from within judge definition JSON."""
        heuristics = []
        for jheuristic in jheuristics:
            heuristic = component.Heuristic()
            heuristic.name = self._must_get(jheuristic, 'name')
            heuristic.desc = self._must_get(jheuristic, 'desc')
            heuristic.criterion_id = self._must_get(jheuristic, 'criterion')

            jlens = self._must_get(jheuristic, 'lens')
            self._parse_function(heuristic.lens, jlens, 
                lens_functions, 'LensFunction', "lens function")
            heuristic.lens.id = jlens.get('id', None) if hasattr(jlens, 'get') else None
            
            jmaps = self._must_get(jheuristic, 'maps')
            for jmap in jmaps:
                map = component.Map()
                self._parse_function(map, jmap, 
                    map_functions, 'MapFunction', "map function")
                heuristic.maps.append(map)

            jreduce = self._must_get(jheuristic, 'reduce')
            self._parse_function(heuristic.reduce, jreduce, 
                reduce_functions, 'ReduceFunction', "reduce function")

            jreduced_maps = jheuristic.get('reduced_maps', [])
            for jmap in jreduced_maps:
                map = component.Map()
                self._parse_function(map, jmap, 
                    map_functions, 'MapFunction', "reduced map function")
                heuristic.reduced_maps.append(map)

            heuristics.append(heuristic)
        return heuristics

    
    # ------------------------------------------------------------------------
    
    
    def _parse_function(self, func, jfunction, stdmodule, baseclsname, desc):
        """
        Fill in func config component.Function object from JSON jfunction.
        Uses classes from standard module specified (dynamic class name),
        or if specified as dotted path uses class specified.
        Verifies and instantiates requested function.
        Example supported forms:
            {"fn": "funcname", "config": {"foo":1, ...}}
            {"fn": "full.path.to.class", "config": {"foo":1, ...}}
            {"fn": "funcname"}
            {"fn": "full.path.to.class"}
            {"fn": "class", "module": "full.path.to.module" }
            "funcname"
            "full.path.to.class"
        """
        if getattr(jfunction, 'items', False): # (dict-like?)
            func.function_id = self._must_get(jfunction, 'fn')
            if jfunction.get('module'):
                func.function_id = jfunction['module'] + '.' + func.function_id
            func.config = jfunction.get('config', dict())
        else:
            func.function_id = jfunction
            func.config = {}
        func.function = self._make_function(func.function_id, func.config, stdmodule, baseclsname, desc)

    def _make_function(self, funcid, config, stdmodule, baseclsname, desc):
        """
        Make/return a config component.Function object requested as funcid.
        Uses classes from standard module specified (dynamic class name),
        or if specified as dotted path uses class specified.
        """
        if '.' in funcid:
            funccls = self._load_class(funcid, desc)
        else:
            try:
                funccls = getattr(stdmodule, '{0}_{1}'.format(baseclsname, funcid))
            except AttributeError as e:
                raise error.ConfigValueError(u"Unknown {0} '{1}'".format(desc, funcid))
        func = funccls(config)
        func.app_context = self._app_context
        return func
        
    def _must_get(self, d, key):
        """Get required keyed element of dictionary, or report error if not present."""
        if key not in d:
            raise error.ConfigIncompleteError(u"Missing key '{0}' under: {1}".format(key, d))
        return d[key]


# ----------------------------------------------------------------------------


class Loader_YAML(Loader):
    """
    Loads config from YAML file-like object.
    
    This current implementation "cheats" by:
     Loading YAML, dumping YAML as JSON string, loading via JSON loader.
    This is fine only because our current tournament file format can be
    directly expressed in JSON.

    Eventually the Loader_JSON class should be turned into a straight up
    JSON loader, and the actual parsing of loaded raw tournament object data
    into components should be in a shared class used by all 
    dialect-specific loaders.
    """
    
    def __init__(self):
        self._f = None
        self._tournament = None
        self._app_context = None   # opaque obj for app to pass data to dynamic functions
    
    def set_file(self, f):
        """Set file-like object to load from."""
        self._f = f
    
    def set_app_context(self, app_context):
        """
        Set new app context opaque obj, for communicating between app and internals.
        Useful for e.g. config information used by custom function extensions.
        """
        self._app_context = app_context
        
    def load_tournament(self):
        """Load, parse, verify, and return Tournament object."""
        try:
            loaded_yaml = yaml.load(self._f)
        except ValueError as e:
            raise error.ConfigSyntaxError("Invalid YAML detected: {0!r}".format(e))

        # Dump loaded YAML as JSON string, then load using Loader_JSON:
        json_str = json.dumps(loaded_yaml)
        fjson = StringIO.StringIO(json_str)
        json_loader = Loader_JSON()
        json_loader.set_file(fjson)
        json_loader.set_app_context(self._app_context)
        return json_loader.load_tournament()

