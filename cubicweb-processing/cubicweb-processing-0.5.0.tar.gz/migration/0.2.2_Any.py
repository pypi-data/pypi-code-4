# value is no more required
if 'ParameterValueFloat' in schema:
    sync_schema_props_perms('ParameterValueFloat')
    sync_schema_props_perms('ParameterValueInt')
    sync_schema_props_perms('ParameterValueString')
    sync_schema_props_perms('value_file')
