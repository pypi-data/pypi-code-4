# postcreate script. You could setup a workflow here for example
wf = add_workflow('task workflow', 'Task')
todo = wf.add_state(_('todo'), initial=True)
inprogress = wf.add_state(_('in-progress'))
done = wf.add_state(_('done'))
wf.add_transition(_('done'), (todo, inprogress), done, ('managers', 'owners'))
wf.add_transition(_('start'), todo, inprogress, ('managers', 'owners'))

commit()
