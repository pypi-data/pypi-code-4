# -*- coding: utf-8 -*-
"""
Temperature
- t -
(oC)	Density
- -
(kg/m3)	Specific heat capacity
- cp -
(kJ/kg.K)	Thermal conductivity
- k -
(W/m.K)	Kinematic viscosity
- ν -
x 10-6 (m2/s)	Expansion coefficient
- b -
x 10-3 (1/K)	Prandtl's number
- Pr -

T       density cp      k       nu      b       Pr
-150 	2.793 	1.026 	0.0116 	3.08 	8.21 	0.76
-100 	1.980 	1.009 	0.0160 	5.95 	5.82 	0.74
-50 	1.534 	1.005 	0.0204 	9.55 	4.51 	0.725
0 	1.293 	1.005 	0.0243 	13.30 	3.67 	0.715
20 	1.205 	1.005 	0.0257 	15.11 	3.43 	0.713
40 	1.127 	1.005 	0.0271 	16.97 	3.20 	0.711
60 	1.067 	1.009 	0.0285 	18.90 	3.00 	0.709
80 	1.000 	1.009 	0.0299 	20.94 	2.83 	0.708
100 	0.946 	1.009 	0.0314 	23.06 	2.68 	0.703
120 	0.898 	1.013 	0.0328 	25.23 	2.55 	0.70
140 	0.854 	1.013 	0.0343 	27.55 	2.43 	0.695
160 	0.815 	1.017 	0.0358 	29.85 	2.32 	0.69
180 	0.779 	1.022 	0.0372 	32.29 	2.21 	0.69
200 	0.746 	1.026 	0.0386 	34.63 	2.11 	0.685
250 	0.675 	1.034 	0.0421 	41.17 	1.91 	0.68
300 	0.616 	1.047 	0.0454 	47.85 	1.75 	0.68
350 	0.566 	1.055 	0.0485 	55.05 	1.61 	0.68
400 	0.524 	1.068 	0.0515 	62.53 	1.49 	0.68



Common Pressure Units frequently used as alternative to "one Atmosphere"

    76 Centimeters (760 mm) of Mercury
    29.921 Inches of Mercury
    10.332 Meters of Water
    406.78 Inches of Water
    33.899 Feet of Water
    14.696 Pound-Force per Square Inch
    2116.2 Pounds-Force per Square Foot
    1.033 Kilograms-Force per Square Centimeter
    101.33 Kilopascal


Density of Dry Air

The density of dry air can be expressed as:

    ρa = 0.0035 pa / T         (1)

    where

    ρa = density dry air (kg/m3)

    pa = partial pressure of air (Pa, N/m2)

    T = absolute dry bulb temperature (K)

Density of Water Vapor

The density of water vapor can be expressed as:

    ρw = 0.0022 pw / T         (2)

    where

    pw = partial pressure water vapor (Pa, N/m2)

    ρw = density water vapor (kg/m3)

    T = absolute dry bulb temperature (K)

Density of Moist Air - an Air Vapor Mixture

    ρ = ρda (1 + x) / (1 + 1.609 x )         (6)





Temperature 	Saturation Pressure
(N/m2) 	Humidity ratio at Saturation
(kgH2O/kgdry air) 	Specific Volume 	Specific Enthalpy 	Specific Entropy
(J/K.kgdry air)
oC 	oF 	Dry Air
(m3/kg) 	 Saturated Mixture
(m3/kg) 	Dry Air
(kJ/kgdry air) 	Saturated Mixture
(kJ/kgdry air)
-40 	-40 	12.84 	0.000079 	0.660 	0.660 	-40.2 	-40.0 	-90.7
-30 	-22 	38 	0.00023 	0.688 	0.688 	-30.2 	-29.6 	-46.7
-25 	-13 	63.25 	0.00039 	0.702 	0.703 	-25.2 	-24.2 	-24.7
-20 	-4 	103.2 	0.00064 	0.716 	0.717 	-20.1 	-18.5 	-2.2
-15 	5 	165.2 	0.0010 	0.731 	0.732 	-15.1 	-12.6 	21.2
-10 	14 	259.2 	0.0016 	0.745 	0.747 	-10.1 	-6.1 	46.1
-5 	23 	401.5 	0.0025 	0.759 	0.762 	-5.0 	1.2 	76.4
0 	32 	610.8 	0.0038 	0.773 	0.778 	0 	9.5 	104.1
5 	41 	871.9 	0.0054 	0.788 	0.794 	5.0 	18.6 	137.4
10 	50 	1227 	0.0077 	0.802 	0.812 	10.1 	29.5 	175.4
15 	59 	1704 	0.011 	0.816 	0.830 	15.1 	42.9 	220.2
20 	68 	2337 	0.015 	0.830 	0.850 	20.1 	58.2 	273.3
25 	77 	3167 	0.020 	0.844 	0.872 	25.2 	76.1 	337.4
30 	86 	4243 	0.027 	0.859 	0.896 	30.2 	99.2 	415.6
35 	95 	5623 	0.037 	0.873 	0.924 	35.2 	130.1 	512.2
40 	104 	7378 	0.049 	0.887 	0.957 	40.2 	166.4 	532.3
45 	113 	9585 	0.065 	0.901 	0.995 	45.3 	213.2 	783.1
50 	122 	12339 	0.087 	0.915 	1.042 	50.3 	275.9 	975.3
55 	131 	14745 	0.12 	0.929 	1.1 	55.3 	367.6 	1221
60 	140 	19925 	0.15 	0.944 	1.175 	60.4 	452.1 	1544
65 	149 	25014 	0.21 	0.958 	1.272 	65.4 	615.7 	1974
70 	158 	31167 	0.28 	0.972 	1.404 	70.4 	806.8 	2565
75 	167 	38554 	0.38 	0.986 	1.592 	75.5 	1078 	3413
80 	176 	47365 	0.55 	1 	1.879 	80.5 	1537 	4711
85 	185 	57809 	0.84 	1.015 	2.363 	85.5 	2317 	6893
90 	194 	70112 	  	1.03 	3.340 	  	3876 	11281




U.S Standard Atmosphere Air Properties in SI Units

based on the following levels bewteen which one interpolates linearly:
    geopot. Höhe h
in m 	geometr. Höhe z
in m 	Temperatur T
in °C 	Luftdruck p
in Pa
0 	0 	15 	101.325
11.000 	11.019 	−56,5 	22.632
20.000 	20.063 	−56,5 	5.474,9
32.000 	32.162 	−44,5 	868,02
47.000 	47.350 	−2,5 	110,91
51.000 	51.413 	−2,5 	66,939
71.000 	71.802 	−58,5 	3,9564
84.852 	86.000 	−86,2 	0,3734


Geo potential Altitude above Sea Level
- h -
(m) 	Temperature
- t -
(oC) 	Acceleration of Gravity
- g -
(m/s2) 	Absolute Pressure
- p -
(104 N/m2) 	Density
- ρ -
(10-1 kg/m3) 	Dynamic Viscosity
- μ -
(10-5 N.s/m2)
-1000 	21.50 	9.810 	11.39 	13.47 	1.821
0 	15.00 	9.807 	10.13 	12.25 	1.789
1000 	8.50 	9.804 	8.988 	11.12 	1.758
2000 	2.00 	9.801 	7.950 	10.07 	1.726
3000 	-4.49 	9.797 	7.012 	9.093 	1.694
4000 	-10.98 	9.794 	6.166 	8.194 	1.661
5000 	-17.47 	9.791 	5.405 	7.364 	1.628
6000 	-23.96 	9.788 	4.722 	6.601 	1.595
7000 	-30.45 	9.785 	4.111 	5.900 	1.561
8000 	-36.94 	9.782 	3.565 	5.258 	1.527
9000 	-43.42 	9.779 	3.080 	4.671 	1.493
10000 	-49.90 	9.776 	2.650 	4.135 	1.458
15000 	-56.50 	9.761 	1.211 	1.948 	1.422
20000 	-56.50 	9.745 	0.5529 	0.8891 	1.422
25000 	-51.60 	9.730 	0.2549 	0.4008 	1.448
30000 	-46.64 	9.715 	0.1197 	0.1841 	1.475
40000 	-22.80 	9.684 	0.0287 	0.03996 	1.601
50000 	-25 	9.654 	0.007978 	0.01027 	1.704
60000 	-26.13 	9.624 	0.002196 	0.003097 	1.584
70000 	-53.57 	9.594 	0.00052 	0.0008283 	1.438
80000 	-74.51 	9.564 	0.00011 	0.0001846 	1.321
"""

