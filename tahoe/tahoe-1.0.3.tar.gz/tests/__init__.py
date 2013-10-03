import sys
from tahoe.tests import TahoeTestCase
from app import TestTahoeApplication

sys.stderr.write("""

     myssshhssssd.    `h.     `/shs/`  `/ohs/.    :ososyy+-   `/ohy++syo
    -s    mM`   s.    sMd       sM/      :My    :do`    `+Nh.   :Mh   .y
          mM`        /m/Ms      -M/      :My   :Ms        :NN.  :Mh   .
          mM`       .N. oM/     -Ms//////sMy   dM.         hM-  :MmssyN
          mM`      `dssssdN.    -M/      :My   yMy         dN.  :Mh   +
          mM`      ys    .NN`   +M/      :My   `hMs`      om:   :Mh    //
        :/NM+/  `/sN+.   `sMd/-/dMd/`  `/sMm/-   -ydhooooy/   `/sMNoooyN.

     [ Tests will free you! FFFFFFFFUUUUU.... ]

""")
sys.stderr.flush()

test_app = TestTahoeApplication()
test_app.setup()
TahoeTestCase.register_tahoe_application(test_app)
