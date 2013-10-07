
for etype in ('VersionedFile', 'Revision',
              'DeletedVersionContent', 'VersionContent'):
    # may be already in. Or not...
    add_relation_definition(etype, 'require_permission', 'CWPermission')

rql('SET X require_permission P WHERE '
    'R require_permission P, X patch_revision R, '
    'NOT X require_permission P')
commit()
