sync_schema_props_perms('Repository')
sync_schema_props_perms('hosted_by')
sync_schema_props_perms('public_key')

for msc in rql('MercurialServerConfig X').entities():
    if msc.base_url.endswith('/'):
        msc.cw_set(base_url=msc.base_url.rstrip('/'))

sync_schema_props_perms('MercurialServerConfig')
