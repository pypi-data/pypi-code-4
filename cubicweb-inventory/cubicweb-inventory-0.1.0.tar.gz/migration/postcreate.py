create_entity('CWGroup', name=u'staff')

device_wf = add_workflow(_('default Device workflow'), 'Device')

operational = device_wf.add_state(_('operational'), initial=True)
broken = device_wf.add_state(_('broken'))

fail = device_wf.add_transition(_('fail'), operational, broken,
                                ('managers', 'owners', 'staff'))
repair = device_wf.add_transition(_('repair'), broken, operational,
                                  ('managers', 'owners', 'staff'))


devicemodel_wf = add_workflow(_('default DeviceModel workflow'), 'DeviceModel')

on_market = devicemodel_wf.add_state(_('on the market'), initial=True)
deprecated = devicemodel_wf.add_state(_('deprecated'))

depreccate = devicemodel_wf.add_transition(_('deprecate'), on_market, deprecated,
                                           ('managers', 'owners', 'staff'))



