

import lotus_core
import sys

lts = lotus_core.create_lotus("dMatrix")

print type(lts)
lts.read_in_file(sys.argv[1])
lts.show()
lts.guess_h_core()
lts.scf_py()
#fxyz = lts.cal_force_py()
#for i in range(len(fxyz)/3):
#  print "i=",i," fxyz ",fxyz[i*3+0],fxyz[i*3+1],fxyz[i*3+2]


