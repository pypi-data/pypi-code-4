from collections import namedtuple

# Radio Front End modes

DC = 'direct_conversion'
SH = 'super_heterodyne'
HR = 'high_resolution'
DD = 'direct_digitization'
IQIN = 'iq_input'


RFEMode = namedtuple('RFEMode', """
    min_tunable
    max_tunable
    vrt_format
    usable_bw
    """, "Radio Front-End Mode properties")
