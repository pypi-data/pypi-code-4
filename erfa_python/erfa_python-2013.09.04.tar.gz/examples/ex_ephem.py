'''ephemerid example

TODO:
   * add refraction,
   * latitude,
   * diurnal aberration,
   * parallax
'''
import math
import erfa

# observer location
latitude = '-18:57:03' #South
longitude = '-47:38:25' #East
altitude = 1258.0

# site terrestrial coordinates (WGS84)
latnd = -18
latnm = 57
slatn = 3
lonwd = +47
lonwm = 38
slonw = 25.
hm = 1258.0

# transform to geocentric
phi = erfa.af2a(latnd, latnm, slatn)
elon = erfa.af2a(lonwd, lonwm, slonw)
xyz = erfa.gd2gc(1, elon, phi, hm)
u = math.hypot(xyz[0], xyz[1])
v = xyz[2]

# Time
UTC = '2013/08/26T09:52:05'
# UTC
utc1, utc2 = erfa.dtf2d(2013,8,26,9,52,5.0)
# TAI
tai1, tai2 = erfa.utctai(utc1, utc2)
# TT
tt1, tt2 = erfa.taitt(tai1, tai2)
# TCG
tcg1, tcg2 = erfa.tttcg(tt1, tt2)
# UT1-UTC from IERS
dut = .1
# UTC -> UT1
ut11, ut12 = erfa.utcut1(utc1, utc2, dut)

# Extract fraction for TDB-TT calculation, later.
ut = math.fmod(math.fmod(ut11,1.0)+math.fmod(ut12,1.0),1.0)

# TDB-TT (using TT as a substitute for TDB).
dtr = erfa.dtdb(tt1, tt2, ut, elon, u, v)
# TDB
tdb1, tdb2 = erfa.tttdb(tt1, tt2, dtr)
# TCB
tcb1, tcb2 = erfa.tdbtcb(tdb1, tdb2)
print(tdb1, tdb2)
print(erfa.fame03(tdb1+tdb2))
