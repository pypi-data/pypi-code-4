rset = rql('Workflow X WHERE X name "task workflow"')
if rset:
    wf = rset.get_entity(0, 0)
    inprogress = wf.add_state(_('in-progress'))
    wf.add_transition(_('start'), wf.state_by_name('todo'), inprogress)
    inprogress.set_relations(allowed_transition=wf.transition_by_name('done'))


sync_schema_props_perms(('Task', 'start', 'Datetime'))
sync_schema_props_perms(('Task', 'stop', 'Datetime'))
