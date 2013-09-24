# -*- coding: UTF-8 -*-
# all objects() from table users_authority:
loader.save(create_users_authority(1,7,6))
loader.save(create_users_authority(2,7,5))
loader.save(create_users_authority(3,6,5))

loader.flush_deferred_objects()
