wf = get_workflow_for('Task')
for trname in ('done', 'start'):
    tr = wf.transition_by_name(trname)
    tr.set_permissions(('managers', 'owners'))
