#!/usr/bin/env python

from morton import (
    get_latlong_morton,
    get_morton,
    )

print get_morton(1,1)
print get_morton(1,2)
print get_morton(2,1)
print get_morton(2,2)

print get_latlong_morton(26.6615, -80.26)
print get_latlong_morton(26.679, -80.2037)
