# -*- coding: UTF-8 -*-
# all objects() from table newcomers_competence:
loader.save(create_newcomers_competence(1,7,1,1,10))
loader.save(create_newcomers_competence(2,6,2,2,5))
loader.save(create_newcomers_competence(3,5,3,3,4))
loader.save(create_newcomers_competence(4,7,4,4,6))
loader.save(create_newcomers_competence(5,6,5,5,2))
loader.save(create_newcomers_competence(6,5,6,1,10))
loader.save(create_newcomers_competence(7,7,7,2,5))

loader.flush_deferred_objects()
