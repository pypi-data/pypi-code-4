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

"""cubicweb-processing schema"""


from yams.buildobjs import EntityType, SubjectRelation, Float, String, Int
from yams.constraints import RegexpConstraint

from cubicweb.schema import WorkflowableEntityType, RQLConstraint, ERQLExpression, RRQLExpression


rel_perms_of_subject = {
    'read':   ('managers', 'users', 'guests',),
    'add':    ('managers', RRQLExpression('U has_update_permission S'),),
    'delete': ('managers', RRQLExpression('U has_update_permission S'),),
    }


rel_perms_of_object = {
    'read':   ('managers', 'users', 'guests',),
    'add':    ('managers', RRQLExpression('U has_update_permission O'),),
    'delete': ('managers', RRQLExpression('U has_update_permission O'),),
    }


class Executable(EntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests',),
        'update': ('managers', ERQLExpression('NOT R executable X')),
        'delete': ('managers', 'owners'),
        'add': ('managers', 'users',)
        }
    name = String(required=True, maxsize=256)


same_lang_cstr = RQLConstraint('S wlang L, O language L')

class RunChain(WorkflowableEntityType):
    name = String(maxsize=128, description=_('a name for convenience purposes'))
    # UI relation, allowing to pick preselected executables from the wiring view
    uses_executable = SubjectRelation('Executable', cardinality='**', 
                                      __permissions__=rel_perms_of_subject)
    has_runs = SubjectRelation('Run', cardinality='*?', composite='subject',
                               __permissions__=rel_perms_of_subject)
    wlang = SubjectRelation('WiringLanguage', cardinality='??',
                            inlined=True, composite='subject',
                            __permissions__=rel_perms_of_subject)
    wiring = SubjectRelation('Wiring', cardinality='??', inlined=True,
                             composite='subject', constraints=[same_lang_cstr],
                             __permissions__=rel_perms_of_subject)


class Run(WorkflowableEntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests',),
        'update': ('managers', ERQLExpression(
            'NOT EXISTS(X in_state S1) OR EXISTS(X in_state S2,'
            ' S2 name IN ("wfs_run_init", "wfs_run_ready"))')),
        'delete': ('managers', 'owners'),
        'add': ('managers', 'users',)
        }
    executable = SubjectRelation(
        'Executable', cardinality='1*', inlined=True, constraints=[
            RQLConstraint('NOT EXISTS(PD parameter_of O, PD param_type "input",'
                          ' NOT EXISTS(PV param_def PD, PV value_of_run S))',
                          msg=_('missing input parameter values')),
            ],
        __permissions__={
            'read': ('managers', 'users', 'guests',),
            'add': ('managers', 'users'), # if I can view an Executable, I can run it
            'delete': ('managers', )},
        description=_('executable used by this Run'))


pdef_of_readable_exe = ERQLExpression('U has_read_permission E, X parameter_of E')
pdef_of_updatable_exe = ERQLExpression('U has_update_permission E, X parameter_of E')

class ParameterDefinition(EntityType):
    __permissions__ = {
        'read':   ('managers', pdef_of_readable_exe),
        'add':    ('managers', 'users'),
        'update': ('managers', pdef_of_updatable_exe),
        'delete': ('managers', pdef_of_updatable_exe),
        }
    name = String(maxsize=256, required=True, constraints=[
        RegexpConstraint('^[a-zA-Z0-9_]+$')])
    value_type = String(required=True, internationalizable=True,
                        vocabulary=(_('Float'), _('Int'), _('String'), _('File')))
    param_type = String(required=True, internationalizable=True,
                        vocabulary=(_('input'), _('output')))
    description = String()
    parameter_of = SubjectRelation('Executable', cardinality='1*',
                                   inlined=True, composite='object',
                                   __permissions__=rel_perms_of_object,
                                   constraints=[
        RQLConstraint('NOT EXISTS(R executable O)', msg=_(
                    "can't modify parameters of an executable which is already used in a run")),
        RQLConstraint('S name N, NOT EXISTS('
                      ' NOT(S identity PD2), PD2 parameter_of O, PD2 name N)',
                      msg=_('parameter name is already used')),],)



pval_of_readable_run = ERQLExpression(
    'U has_read_permission R, X value_of_run R')
pval_of_updatable_run = ERQLExpression(
    'U has_update_permission R, X value_of_run R')

class _ParameterValue(EntityType):
    __abstract__ = True
    __permissions__ = {
        'read':   ('managers', pval_of_readable_run),
        'add':    ('managers', 'users'),
        'update': ('managers', pval_of_updatable_run),
        'delete': ('managers', ),
        }
    value_of_run = SubjectRelation(
        'Run',
        cardinality='1*',
        composite='object',
        constraints=[
            RQLConstraint(
                'O executable E, S param_def PD, EXISTS(PD parameter_of E)',
                msg=_('cannot find such a parameter for this executable')),
            RQLConstraint(
                'O executable E, S param_def PD, '
                'NOT EXISTS(V value_of_run O, NOT S identity V, '
                           'V param_def PD)',
                msg=_('this parameter has several values')),
            ],
        inlined=True,
        __permissions__={'read': ('managers', 'users', 'guests'),
                         'add': ('managers',
                                 RRQLExpression('U has_update_permission O')),
                         'delete': ('managers', )})
    from_run = SubjectRelation(
        'Run', cardinality='?*', inlined=True,
        description=_('run from which to copy into this input parameter value '
                      'when chaining runs'),
        constraints=[RQLConstraint('O executable E, OD parameter_of E, '
                                   'OD value_type T, OD param_type "output", '
                                   'S param_def PD, PD value_type T',
                                   msg=_('specified run has no output '
                                         'parameter of the right type'))],
        __permissions__=rel_perms_of_subject
        )

    from_output = SubjectRelation(
        'ParameterDefinition', cardinality='?*', inlined=True,
        description=_('output parameter definition to copy into this input parameter '
                      'value when chaining runs'),
        constraints=[RQLConstraint('O value_type T, S param_def PD, PD value_type T',
                                   msg=_('copied output parameter has wrong value type')),
                     RQLConstraint('S from_run R, R executable E, O parameter_of E',
                                   msg=_('copied output parameter is unrelated to source run')),
                     RQLConstraint('O param_type "output", S param_def PD, PD param_type "input"',
                                   msg=_('parameter copy must from an output to an input')),
                     ],
        __permissions__=rel_perms_of_subject
        )

param_def_perms = {
    'read':   ('managers', 'users', 'guests',),
    'add':    ('managers', 'users'),
    'delete': ('managers', ),
    }

class ParameterValueFloat(_ParameterValue):
    value = Float()
    param_def = SubjectRelation(
        'ParameterDefinition', cardinality='1*', inlined=True, composite='object',
        constraints=[RQLConstraint('O value_type "Float"')],
        __permissions__=param_def_perms)


class ParameterValueInt(_ParameterValue):
    value = Int()
    param_def = SubjectRelation(
        'ParameterDefinition', cardinality='1*', inlined=True, composite='object',
        constraints=[RQLConstraint('O value_type "Int"')],
        __permissions__=param_def_perms)


class ParameterValueString(_ParameterValue):
    value = String()
    param_def = SubjectRelation(
        'ParameterDefinition', cardinality='1*', inlined=True, composite='object',
        constraints=[RQLConstraint('O value_type "String"')],
        __permissions__=param_def_perms)


class ParameterValueFile(_ParameterValue):
    value_file = SubjectRelation('File', cardinality='?*', inlined=True,
                                 __permissions__=rel_perms_of_subject)
    param_def = SubjectRelation(
        'ParameterDefinition', cardinality='1*', inlined=True, composite='object',
        constraints=[RQLConstraint('O value_type "File"')],
        __permissions__=param_def_perms)
