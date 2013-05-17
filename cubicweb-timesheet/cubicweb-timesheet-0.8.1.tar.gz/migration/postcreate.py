# ResourceType person
restype = rql('INSERT Resourcetype RT: RT title "person"').rows[0][0]

# Activity workflow
wf = add_workflow('activities default workflow', 'Activity')
pending    = wf.add_state(_('pending'), initial=True)
validated  = wf.add_state(_('validated'))
wf.add_transition(_('validate'), pending, validated, ('managers',))


