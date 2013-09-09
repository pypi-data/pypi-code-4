add_attribute('Executable', 'name')
drop_relation_type('executable_of')
drop_entity_type('Program')
add_attribute('ParameterDefinition', 'param_type')
add_attribute('ParameterDefinition', 'value_type')
rql('SET X value_type "Float", X param_type "input" WHERE X is ParameterDefinition')
add_attribute('ParameterDefinition', 'description')
add_relation_type('value_of_run')
add_relation_type('from_output')

add_entity_type('ParameterValueInt')
add_entity_type('ParameterValueFloat')
add_entity_type('ParameterValueString')
add_entity_type('ParameterValueFile')


MAP = {}
for objdef in rql('ObjectiveDefinition X').entities(0):
    objdef.complete()
    e = session.create_entity('ParameterDefinition',
                              name=objdef.name,
                              value_type=objdef.value_type,
                              param_type=u'output',
                              parameter_of=objdef.objective_of)
    MAP[obdef.eid] = e.eid

for otype in ('Int', 'Float', 'String'):
    etype = 'ObjectiveValue%s' % otype
    if etype in schema:
        for ovalue in rql('%s X' % etype).entities(0):
            session.create_entity('ParameterValue%s' % etype,
                                  value=ovalue.value,
                                  values_for_run=ovalue.reverse_obj_values,
                                  from_run=ovalue.from_run,
                                  from_output=ovalue.from_obj and MAP[ovalue.from_obj[0].eid] or None,
                                  param_def=MAP[ovalue.obj_def[0].eid])
        drop_entity_type(etype)
if 'ObjectiveValue' in schema:
    for ovalue in rql('ObjectiveValue X').entities(0):
        session.create_entity('ParameterValueFloat',
                              value=ovalue.value,
                              values_for_run=ovalue.reverse_obj_values,
                              from_run=ovalue.from_run,
                              from_output=ovalue.from_obj and MAP[ovalue.from_obj[0].eid] or None,
                              param_def=MAP[ovalue.obj_def[0].eid])
    drop_entity_type('ObjectiveValue')
if 'ObjectiveValueFile' in schema:
    for ovalue in rql('ObjectiveValueFile X').entities(0):
        session.create_entity('ParameterValueFile',
                              value_file=ovalue.value_file,
                              values_for_run=ovalue.reverse_obj_values,
                              from_run=ovalue.from_run,
                              from_output=ovalue.from_obj and MAP[ovalue.from_obj[0].eid] or None,
                              param_def=MAP[ovalue.obj_def[0].eid])
    drop_entity_type('ObjectiveValueFile')

drop_entity_type('ObjectiveDefinition')

if 'ParameterValue' in schema:
    for ovalue in rql('ParameterValue X').entities(0):
        session.create_entity('ParameterValueFloat',
                              value=ovalue.value,
                              values_for_run=ovalue.reverse_param_values,
                              param_def=ovalue.param_def[0].eid)
    drop_entity_type('ParameterValue')

if 'Study' in schema:
    rename_entity_type('Study', 'RunChain')

add_cube('wireit')

sync_schema_props_perms('parameter_of')
sync_schema_props_perms('Run')
sync_schema_props_perms('executable')

sync_schema_props_perms('Run')
sync_schema_props_perms('ParameterValueInt', syncprops=False)
sync_schema_props_perms('ParameterValueFloat', syncprops=False)
sync_schema_props_perms('ParameterValueString', syncprops=False)
sync_schema_props_perms('ParameterValueFile', syncprops=False)
sync_schema_props_perms('Executable', syncprops=False)
sync_schema_props_perms('ParameterDefinition', syncprops=False)
sync_schema_props_perms('param_def')
