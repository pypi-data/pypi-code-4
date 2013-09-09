# copyright 2012-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-processing entity's classes"""

from itertools import repeat, izip, chain
from json import dumps, loads

from logilab.common.decorators import cachedproperty

from cubicweb import ValidationError
from cubicweb.entities import AnyEntity, fetch_config


class Executable(AnyEntity):
    __regid__ = 'Executable'

    def add_input(self, name, value_type):
        return self._cw.create_entity(
            'ParameterDefinition', param_type=u'input', parameter_of=self,
            value_type=value_type, name=name)

    def add_output(self, name, value_type):
        return self._cw.create_entity(
            'ParameterDefinition', param_type=u'output', parameter_of=self,
            value_type=value_type, name=name)

    @cachedproperty
    def all_defs(self):
        return dict((pdef.name, pdef)
                    for pdef in self.reverse_parameter_of)

    @property
    def input_defs(self):
        return dict((name, pdef)
                    for name, pdef in self.all_defs.iteritems()
                    if pdef.param_type==u'input')

    @property
    def output_defs(self):
        return dict((name, pdef)
                    for name, pdef in self.all_defs.iteritems()
                    if pdef.param_type==u'output')

    def cw_clear_all_caches(self):
        super(Executable, self).cw_clear_all_caches()
        if 'all_defs' in self.__dict__:
            del self.all_defs


class ParameterDefinition(AnyEntity):
    __regid__ = 'ParameterDefinition'

    fetch_attrs, cw_fetch_order = fetch_config(
        ['name', 'value_type', 'parameter_of'],
        mainattr='modification_date', order='ASC')

    @cachedproperty
    def poval_etype(self):
        """Return the name of the class that can represent a value for
        current parameter definition.  Examples: ParameterValueFloat.
        """
        return self.__regid__.replace('Definition', 'Value') + self.value_type

    def typed_value(self, value):
        """
        Returns the given `value` typed as expected according to PO's
        value_type.
        """
        if value is None:
            raise ValueError
        # File case
        if self.value_type == 'File':
            try:
                entity = self._cw.entity_from_eid(int(value))
                assert entity.e_schema.type == 'File'
                return entity
            except (ValueError, AssertionError):
                raise ValueError('incorrect file eid')
        # Other value types
        try:
            return {'Float': float, 'Int': int,
                    'String': unicode}[self.value_type](value)
        except (TypeError, ValueError):
            self.error('unable to convert parameter value %r into type %s '
                       'for variable %s of executable %s', value,
                       self.value_type, self.name, self.exe.dc_title())
            raise

    def create_value(self, value, run, **kwargs):
        if self.value_type != 'File':
            kwargs['value'] = value
        elif value is not None:
            kwargs['value_file'] = value
        kwargs['param_def'] = self
        pval = self._cw.create_entity(self.poval_etype, value_of_run=run,
                                      **kwargs)
        run.cw_clear_relation_cache('value_of_run', 'object') # XXX see #3034699
        return pval

    @cachedproperty
    def exe(self):
        return self.parameter_of and self.parameter_of[0] or None


class _ParameterValueMixin(object):

    @property
    def pdef(self):
        return self.param_def[0]

    @property
    def ptype(self):
        return self.pdef.param_type

    @property
    def vtype(self):
        return self.pdef.value_type

    @property
    def pname(self):
        return self.pdef.name

    def dc_title(self):
        value = self.value
        if self.value is None and self.from_output and self.from_run:
            value = self._cw._(u'[copy of %(output)s from run #%(run)s]') % {
                'output': self.from_output[0].dc_title(), 'run': self.from_run[0].eid}
        return u'%s=%s' % (self.pname, value)

    @property
    def run(self):
        return self.value_of_run[0]


class ParameterValueFloat(_ParameterValueMixin, AnyEntity):
    __regid__ = 'ParameterValueFloat'


class ParameterValueInt(_ParameterValueMixin, AnyEntity):
    __regid__ = 'ParameterValueInt'


class ParameterValueString(_ParameterValueMixin, AnyEntity):
    __regid__ = 'ParameterValueString'


class ParameterValueFile(_ParameterValueMixin, AnyEntity):
    __regid__ = 'ParameterValueFile'

    def dc_title(self):
        return u'%s=%s [%s]' % (self.pname,
                                self.value and self.value.dc_title() or '<no file>',
                                self._cw._('File'))

    @property
    def value(self):
        "Give ParameterValueFile the same api as other ParameterValue instances"
        return self.value_file and self.value_file[0] or None


def replace_entities_by_eids(xvaluedict):
    return dict((k, v.eid if isinstance(v, AnyEntity) else v)
                for k, v in xvaluedict.iteritems())


class RunChain(AnyEntity):
    __regid__ = 'RunChain'

    @property
    def wlang_name(self):
        'Wiring language name associated to current runchain (must be unique)'
        return self._cw._(u'wiring language of runchain %s') % self.eid

    def wiring_language(self):
        modules = []
        types = {'Int': 'number', 'Float': 'number',
                 'String': 'string', 'File': 'file'}
        for exe in self.uses_executable:
            fields = []
            for pdef, def_kind, other_kind in chain(
                izip(exe.input_defs.itervalues(), repeat('input'), repeat('output')),
                izip(exe.output_defs.itervalues(), repeat('output'), repeat('input'))):
                fields.append({
                    'type': types[pdef.value_type],
                    'inputParams': {
                        'name': pdef.name,
                        'label': pdef.description or pdef.name,
                        'required': True,
                        'wirable': True,
                        # always disable output parameter form fields
                        'disabled': def_kind == 'output',
                        'term_type': '%s_%s' % (def_kind, pdef.value_type),
                        'term_allowed_types': ['%s_%s' % (other_kind,
                                                          pdef.value_type)],
                        }
                    })
            container = {'xtype': "WireIt.FormContainer",
                         'title': exe.dc_title(),
                         # to be added in DB ? 'icon': '/data/icon.png',
                         'fields': fields,
                         }
            modules.append({'name': exe.dc_title(),
                            'eid': exe.eid,
                            'container': container})
        return unicode(dumps({'languageName': self.wlang_name,
                              'modules': modules}))

    def _wiring_error(self, msg, **kwargs):
        raise ValidationError(self.eid, {'json': self._cw._(msg) % kwargs})

    def _exec_from_eid(self, eid):
        "XXX to be replaced by a cleaner implementation"
        for executable in self.uses_executable:
            if executable.eid == eid:
                return executable
        self._wiring_error('invalid wiring: unknown executable "%(exe)s"',
                           exe=dc_title)

    def _param_value(self, pdef, module_descr):
        """
        Returns a value from wireit module description `module_descr`, typed
        according to the expected type defined in `pdef`.

        If the parameter `pdef` was not found, raises a ValidationError.
        """
        try:
            # empty value is considered None
            val = module_descr['value'].pop(pdef.name)
        except KeyError:
            self._wiring_error('invalid wiring: parameter "%(name)s" not found',
                               name=pdef.name)
        if val in (u'', u'[wired]'):
            val = None
        try:
            return pdef.typed_value(val)
        except (TypeError, ValueError):
            self._wiring_error('invalid wiring: value of "%(name)s" is '
                               'invalid: %(val)r', name=pdef.name, val=val)

    def _wired_entity(self, wired_entities, wire, src_tgt):
        """
        Helper method that pops an entity in `wired_entities`, which key is in
        wire description dict `wire` in the dict value which key is `src_tgt`.

        Raises a ValidationError if such an entity is not found.
        """
        ekey = (wire[src_tgt]['moduleId'], wire[src_tgt]['terminal'])
        try:
            return wired_entities.pop(ekey)
        except KeyError:
            self._wiring_error('invalid wiring: wire terminal %(term)s was '
                               'not found in known parameters',
                               term=wire[src_tgt])

    def create_runs_from_wiring(self):
        '''
        Create complete Run instances from wiring description, including:

        - Run instances linked to corresponding executable
        - ParameterValue instances linked to their run and an output
          ParameterDefinition if they are wired in the graphical wiring.
        '''
        executables, wired_entities = {}, {}
        wiring = self.wiring[0]
        wdict = loads(wiring.json) # directly from the db since it was just saved there
        self.debug("create_runs_from_wiring - wiring json: %s", wdict)

        wired_terms = set()
        for wire in wdict['wires']:
            wired_terms.add((wire['src']['terminal'], wire['src']['moduleId']))
            wired_terms.add((wire['tgt']['terminal'], wire['tgt']['moduleId']))

        for modid, module in enumerate(wdict['modules']):

            # create Run instances
            try:
                executable = executables[module['eid']]
            except KeyError:
                executable = executables.setdefault(
                    module['eid'], self._exec_from_eid(module['eid']))
            run = self._cw.create_entity('Run', executable=executable,
                                         reverse_has_runs=self)
            self.debug('Created run %s for runchain %s', run, self)

            # create input ParameterValue instances
            pvalues = module['value'].copy()
            for pdef in executable.input_defs.itervalues():
                wired = (pdef.name, modid) in wired_terms
                value = None if wired else self._param_value(pdef, module)
                self.debug('parameter %s wired %s', pdef.name, wired)
                pvalues.pop(pdef.name)
                pval = pdef.create_value(value, run, param_def=pdef)
                self.debug('Created param value %s (value=%s) for runchain %s',
                           pval, pval.value, self)
                if wired:
                    wired_entities[(modid, pdef.name)] = pval

            # create links between input and output parameters
            for pdef in executable.output_defs.itervalues():
                wired = (pdef.name, modid) in wired_terms
                self.debug('output param %s wired %s', pdef.name, wired)
                pvalues.pop(pdef.name)
                if wired:
                    wired_entities[(modid, pdef.name)] = {'from_run': run,
                                                          'from_output': pdef}
            # consistency check: all module values should have been consumed
            if pvalues:
                self._wiring_error('invalid wiring: following parameters '
                                   'are not defined by any executable used by '
                                   'current runchain %(pos)s', pos=pvalues.keys())

        # create (Run, output ParameterDefinition) <-> ParameterValue relations
        self.debug('wired parameter values: %s', wired_entities)
        for wire in wdict['wires']:
            pval = self._wired_entity(wired_entities, wire, 'tgt')
            pval_rels = self._wired_entity(wired_entities, wire, 'src')
            pval.cw_set(**pval_rels)

        # consistency check: all wired entities should have been consumed
        if wired_entities:
            self._wiring_error('invalid wiring: wires are not consistent with '
                               'wired input and output parameters.')


class Run(AnyEntity):
    __regid__ = 'Run'

    @property
    def exe(self):
        return self.executable[0]

    def dc_title(self):
        return u'Run for `%s`' % self.exe.dc_title()

    @property
    def input_values(self):
        return [v for v in self.reverse_value_of_run if v.ptype == 'input']

    @property
    def output_values(self):
        return [v for v in self.reverse_value_of_run if v.ptype == 'output']

    @cachedproperty
    def ivalue_dict(self):
        '''
        Returns a dictionary of the values of the parameters of the run.

        To be called only when the run is ready to run (all parameters have a
        significative value, not a going-to-be-copied-from-an-output one).
        '''
        return dict((pval.pname, pval.value) for pval in self.input_values)

    def ivalue(self, name):
        try:
            return self.ivalue_dict[name]
        except KeyError:
            err_msg = self._cw._('no parameter found with name %s') % name
            raise ValueError(err_msg)

    def ivalue_entity(self, name):
        for ivalue in self.input_values:
            if ivalue.pname == name:
                return ivalue
        err_msg = self._cw._('no parameter found with name %s') % name
        raise ValueError(err_msg)

    @cachedproperty
    def ovalue_dict(self):
        'Returns a dictionary (name, value) for the outputs of the run'
        return dict((oval.pname, oval.value) for oval in self.output_values)

    def set_ovalues(self, **actual_outputs):
        """Create an output parameter value for each entry of the
        ParameterDefinition if that entry exists in the `actual_outputs`
        dictionary.
        """
        for obj in self.exe.output_defs.itervalues():
            value = actual_outputs.get(obj.name, None)
            if value is not None:
                obj.create_value(obj.typed_value(value), self)

    def is_ready(self):
        return not any(v.value is None for v in self.input_values)

    def is_complete(self):
        onames = [o.pname for o in self.output_values]
        return all(vname in onames
                   for vname in self.exe.output_defs)

    def __setitem__(self, param_name, param_value):
        param_def = self.exe.all_defs[param_name]
        try:
            pval = self.ivalue_entity(param_name)
        except ValueError:
            param_def.create_value(param_value, self)
        else:
            pval.cw_set(value=param_value)

    def __getitem__(self, param_name):
        try:
            return self.ivalue(param_name)
        except KeyError:
            return self.ovalue_dict[param_name]

    def link_input_to_output(self, input_name, from_run, output_name):
        input_def = self.exe.input_defs[input_name]
        input_def.create_value(None, self,
                               from_run=from_run,
                               from_output=from_run.exe.output_defs[output_name])
