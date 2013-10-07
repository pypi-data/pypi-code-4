# -*- coding: UTF-8 -*-
# all objects() from table newcomers_broker:
loader.save(create_newcomers_broker(1,u'Police'))
loader.save(create_newcomers_broker(2,u'Other PCSW'))

loader.flush_deferred_objects()
