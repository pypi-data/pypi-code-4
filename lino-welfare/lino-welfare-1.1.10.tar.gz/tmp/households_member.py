# -*- coding: UTF-8 -*-
# all objects() from table households_member:
loader.save(create_households_member(1,1,181,112,None,None))
loader.save(create_households_member(2,2,181,113,None,None))
loader.save(create_households_member(3,1,182,114,None,None))
loader.save(create_households_member(4,2,182,117,None,None))
loader.save(create_households_member(5,1,183,115,None,None))
loader.save(create_households_member(6,2,183,118,None,None))

loader.flush_deferred_objects()
