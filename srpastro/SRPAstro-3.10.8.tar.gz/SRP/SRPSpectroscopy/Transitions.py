""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/09/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (05/09/2011) First version.

"""




# Transition list as included in ESO-MIDAS fitlyman package
SRPOVII_18 = "OVII_18"
SRPOVII_21 = "OVII_21"
SRPHeII_256 = "HeII_256"
SRPHeII_303 = "HeII_303"
SRPHeI_515 = "HeI_515"
SRPHeI_522 = "HeI_522"
SRPHeI_537 = "HeI_537"
SRPHeI_584 = "HeI_584"
SRPMgX_609 = "MgX_609"
SRPMgX_624 = "MgX_624"
SRPOIII_702 = "OIII_702"
SRPNeVIII_770 = "NeVIII_770"
SRPNeVIII_780 = "NeVIII_780"
SRPOIV_787 = "OIV_787"
SRPOII_832 = "OII_832"
SRPOIII_832 = "OIII_832"
SRPOII_833 = "OII_833"
SRPOII_834 = "OII_834"
SRPPIII_913 = "PIII_913"
SRPDI_915b = "DI_915b"
SRPDI_915a = "DI_915a"
SRPNII_915 = "NII_915"
SRPHI_915 = "HI_915"
SRPDI_916b = "DI_916b"
SRPHI_916 = "HI_916"
SRPOI_916b = "OI_916b"
SRPDI_916a = "DI_916a"
SRPOI_916a = "OI_916a"
SRPPIII_917 = "PIII_917"
SRPHI_917 = "HI_917"
SRPDI_917 = "DI_917"
SRPOI_918 = "OI_918"
SRPHI_918 = "HI_918"
SRPDI_919 = "DI_919"
SRPOI_919c = "OI_919c"
SRPHI_919 = "HI_919"
SRPOI_919b = "OI_919b"
SRPOI_919a = "OI_919a"
SRPDI_920 = "DI_920"
SRPHI_920 = "HI_920"
SRPHI_920 = "HI_920"
SRPOI_921 = "OI_921"
SRPOI_922 = "OI_922"
SRPDI_922 = "DI_922"
SRPHI_923 = "HI_923"
SRPOI_924 = "OI_924"
SRPOI_925 = "OI_925"
SRPDI_925 = "DI_925"
SRPHI_926 = "HI_926"
SRPOI_929 = "OI_929"
SRPOI_930 = "OI_930"
SRPDI_930 = "DI_930"
SRPHI_930 = "HI_930"
SRPSVI_933 = "SVI_933"
SRPOI_936 = "OI_936"
SRPDI_937 = "DI_937"
SRPHI_937 = "HI_937"
SRPOI_937 = "OI_937"
SRPSVI_994 = "SVI_994"
SRPOI_948 = "OI_948"
SRPDI_949 = "DI_949"
SRPLy_d = "Ly_d"
SRPPIV_950 = "PIV_950"
SRPOI_950 = "OI_950"
SRPNI_953c = "NI_953c"
SRPNI_953b = "NI_953b"
SRPNI_953a = "NI_953a"
SRPNI_954 = "NI_954"
SRPPII_961 = "PII_961"
SRPPII_963 = "PII_963"
SRPNI_963 = "NI_963"
SRPNI_964 = "NI_964"
SRPNI_965 = "NI_965"
SRPOI_971c = "OI_971c"
SRPOI_971b = "OI_971b"
SRPOI_971a = "OI_971a"
SRPDI_972 = "DI_972"
SRPLy_g = "Ly_g"
SRPOI_976 = "OI_976"
SRPCIII_977 = "CIII_977"
SRPOI_988c = "OI_988c"
SRPOI_988b = "OI_988b"
SRPOI_988a = "OI_988a"
SRPNIII_989 = "NIII_989"
SRPNIII_989 = "NIII_989"
SRPSiII_989 = "SiII_989"
SRPPIII_997 = "PIII_997"
SRPSIII_1012 = "SIII_1012"
SRPSiII_1020 = "SiII_1020"
SRPDI_1025 = "DI_1025"
SRPLy_b = "Ly_b"
SRPOI_1025 = "OI_1025"
SRPMgII_1025 = "MgII_1025"
SRPMgII_1026 = "MgII_1026"
SRPOI_1026 = "OI_1026"
SRPOVI_1031 = "OVI_1031"
SRPBeII_1036b = "BeII_1036b"
SRPBeII_1036a = "BeII_1036a"
SRPCII_1036 = "CII_1036"
SRPCIIstar_1037 = "CIIstar_1037"
SRPOVI_1037 = "OVI_1037"
SRPOI_1039 = "OI_1039"
SRPArI_1048 = "ArI_1048"
SRPFeII_1055 = "FeII_1055"
SRPFeII_1062 = "FeII_1062"
SRPSIV_1062 = "SIV_1062"
SRPFeII_1063b = "FeII_1063b"
SRPFeII_1063a = "FeII_1063a"
SRPArI_1066 = "ArI_1066"
SRPFeII_1081 = "FeII_1081"
SRPFeII_1083 = "FeII_1083"
SRPNII_1083 = "NII_1083"
SRPFeII_1096 = "FeII_1096"
SRPFeII_1106 = "FeII_1106"
SRPFeII_1112 = "FeII_1112"
SRPPV_1117 = "PV_1117"
SRPFeII_1121 = "FeII_1121"
SRPFeIII_1122 = "FeIII_1122"
SRPFeII_1125 = "FeII_1125"
SRPFeII_1127 = "FeII_1127"
SRPPV_1128 = "PV_1128"
SRPFeII_1133 = "FeII_1133"
SRPNI_1134c = "NI_1134c"
SRPNI_1134b = "NI_1134b"
SRPNI_1134a = "NI_1134a"
SRPCI_1139 = "CI_1139"
SRPFeII_1142 = "FeII_1142"
SRPFeII_1143 = "FeII_1143"
SRPFeII_1144 = "FeII_1144"
SRPPII_1152 = "PII_1152"
SRPCI_1155 = "CI_1155"
SRPCI_1157a = "CI_1157a"
SRPCI_1157b = "CI_1157b"
SRPMnII_1162 = "MnII_1162"
SRPCI_1188 = "CI_1188"
SRPSIII_1190 = "SIII_1190"
SRPSiII_1190 = "SiII_1190"
SRPCI_1193a = "CI_1193a"
SRPSiII_1193 = "SiII_1193"
SRPCI_1193b = "CI_1193b"
SRPSiIIstar_1194 = "SiIIstar_1194"
SRPMnII_1197 = "MnII_1197"
SRPSiIIstar_1197 = "SiIIstar_1197"
SRPMnII_1199 = "MnII_1199"
SRPNI_1199 = "NI_1199"
SRPNI_1200b = "NI_1200b"
SRPNI_1200a = "NI_1200a"
SRPMnII_1201 = "MnII_1201"
SRPSiIII_1206 = "SiIII_1206"
SRPFeIII_1214 = "FeIII_1214"
SRPDI_1215 = "DI_1215"
SRPLy_a = "Ly_a"
SRPNV_1238 = "NV_1238"
SRPMgII_1239 = "MgII_1239"
SRPMgII_1240 = "MgII_1240"
SRPNV_1242 = "NV_1242"
SRPSII_1250 = "SII_1250"
SRPSII_1253 = "SII_1253"
SRPSiI_1255 = "SiI_1255"
SRPSII_1259 = "SII_1259"
SRPSiII_1260 = "SiII_1260"
SRPFeII_1260 = "FeII_1260"
SRPCI_1260 = "CI_1260"
SRPCIstar_1260a = "CIstar_1260a"
SRPCIstar_1260b = "CIstar_1260b"
SRPCIstar_1261 = "CIstar_1261"
SRPCIstarstar_1261a = "CIstarstar_1261a"
SRPCIstarstar_1261b = "CIstarstar_1261b"
SRPSiIIstar_1264 = "SiIIstar_1264"
SRPSiIIstar_1265 = "SiIIstar_1265"
SRPCI_1276 = "CI_1276"
SRPCIstar_1276 = "CIstar_1276"
SRPCIstarstar_1277a = "CIstarstar_1277a"
SRPCI_1277 = "CI_1277"
SRPCIstar_1277a = "CIstar_1277a"
SRPCIstar_1277b = "CIstar_1277b"
SRPCIstarstar_1277b = "CIstarstar_1277b"
SRPCIstarstar_1277c = "CIstarstar_1277c"
SRPCIstar_1279 = "CIstar_1279"
SRPCI_1280 = "CI_1280"
SRPCIstarstar_1280a = "CIstarstar_1280a"
SRPCIstar_1280a = "CIstar_1280a"
SRPCIstar_1280b = "CIstar_1280b"
SRPCIstarstar_1280b = "CIstarstar_1280b"
SRPSI_1295 = "SI_1295"
SRPTiIII_1295 = "TiIII_1295"
SRPTiIII_1298 = "TiIII_1298"
SRPPII_1301 = "PII_1301"
SRPOI_1302 = "OI_1302"
SRPSiII_1304 = "SiII_1304"
SRPOIstar_1304 = "OIstar_1304"
SRPOIstarstar_1306 = "OIstarstar_1306"
SRPSiIIstar_1309 = "SiIIstar_1309"
SRPNiII_1317 = "NiII_1317"
SRPCI_1328 = "CI_1328"
SRPCIstar_1329a = "CIstar_1329a"
SRPCIstar_1329b = "CIstar_1329b"
SRPCIstar_1329c = "CIstar_1329c"
SRPCIstarstar_1329a = "CIstarstar_1329a"
SRPCIstarstar_1329b = "CIstarstar_1329b"
SRPCII_1334 = "CII_1334"
SRPPIII_1334 = "PIII_1334"
SRPCIIstar_1335b = "CIIstar_1335b"
SRPCIIstar_1335a = "CIIstar_1335a"
SRPClI_1347 = "ClI_1347"
SRPOI_1335 = "OI_1335"
SRPCuII_1358 = "CuII_1358"
SRPBII_1362 = "BII_1362"
SRPCuII_1367 = "CuII_1367"
SRPNiII_1370 = "NiII_1370"
SRPNiII_1393 = "NiII_1393"
SRPSiIV_1393 = "SiIV_1393"
SRPSiIV_1402 = "SiIV_1402"
SRPGaII_1414 = "GaII_1414"
SRPCoII_1424 = "CoII_1424"
SRPNiII_1454 = "NiII_1454"
SRPCoII_1446 = "CoII_1446"
SRPNiII_1467b = "NiII_1467b"
SRPNiII_1467a = "NiII_1467a"
SRPSI_1473 = "SI_1473"
SRPCoII_1480 = "CoII_1480"
SRPNiII_1502 = "NiII_1502"
SRPSiII_1526 = "SiII_1526"
SRPPII_1532 = "PII_1532"
SRPSiIIstar_1533 = "SiIIstar_1533"
SRPCIV_1548 = "CIV_1548"
SRPCIV_1550 = "CIV_1550"
SRPCoII_1552 = "CoII_1552"
SRPCI_1560 = "CI_1560"
SRPCIstar_1560a = "CIstar_1560a"
SRPCIstar_1560b = "CIstar_1560b"
SRPCIstarstar_1561a = "CIstarstar_1561a"
SRPCIstarstar_1561b = "CIstarstar_1561b"
SRPCIstarstar_1561c = "CIstarstar_1561c"
SRPSiI_1562 = "SiI_1562"
SRPCoII_1572 = "CoII_1572"
SRPCoII_1574 = "CoII_1574"
SRPFeII_1588 = "FeII_1588"
SRPZnI_1589 = "ZnI_1589"
SRPGeII_1602 = "GeII_1602"
SRPFeII_1608 = "FeII_1608"
SRPFeII_1611 = "FeII_1611"
SRPFeII_1618star = "FeII_1618star"
SRPFeII_1621star = "FeII_1621star"
SRPSiI_1625 = "SiI_1625"
SRPFeII_1629star2 = "FeII_1629star2"
SRPSiI_1631 = "SiI_1631"
SRPFeII_1634star3 = "FeII_1634star3"
SRPFeII_1636star3 = "FeII_1636star3"
SRPFeII_1639star4 = "FeII_1639star4"
SRPHeII_1640 = "HeII_1640"
SRPCIstar_1656 = "CIstar_1656"
SRPCI_1656 = "CI_1656"
SRPCIstarstar_1657 = "CIstarstar_1657"
SRPCIstar_1657a = "CIstar_1657a"
SRPCIstar_1657b = "CIstar_1657b"
SRPCIstarstar_1658 = "CIstarstar_1658"
SRPAlII_1670 = "AlII_1670"
SRPSiI_1693 = "SiI_1693"
SRPNiII_1703 = "NiII_1703"
SRPMgI_1707 = "MgI_1707"
SRPNiII_1709 = "NiII_1709"
SRPNiII_1741 = "NiII_1741"
SRPMgI_1747 = "MgI_1747"
SRPNiII_1751 = "NiII_1751"
SRPPI_1774 = "PI_1774"
SRPPI_1782 = "PI_1782"
SRPSI_1807 = "SI_1807"
SRPSiII_1808 = "SiII_1808"
SRPMgI_1827 = "MgI_1827"
SRPSiI_1845 = "SiI_1845"
SRPFeI_1851 = "FeI_1851"
SRPAlIII_1854 = "AlIII_1854"
SRPAlIII_1862 = "AlIII_1862"
SRPFeII_1901 = "FeII_1901"
SRPTiII_1910b = "TiII_1910b"
SRPTiII_1910a = "TiII_1910a"
SRPCoII_1941 = "CoII_1941"
SRPCoII_2012 = "CoII_2012"
SRPZnII_2026 = "ZnII_2026"
SRPCoII_2026 = "CoII_2026"
SRPMgI_2026 = "MgI_2026"
SRPCrII_2056 = "CrII_2056"
SRPCoII_2059 = "CoII_2059"
SRPCrII_2062 = "CrII_2062"
SRPZnII_2062 = "ZnII_2062"
SRPCrII_2066 = "CrII_2066"
SRPZnI_2139 = "ZnI_2139"
SRPFeI_2167 = "FeI_2167"
SRPFeII_2234 = "FeII_2234"
SRPFeII_2249 = "FeII_2249"
SRPFeII_2260 = "FeII_2260"
SRPAlI_2264 = "AlI_2264"
SRPCaI_2276 = "CaI_2276"
SRPNiI_2311 = "NiI_2311"
SRPNiI_2320 = "NiI_2320"
SRPFeII_2328star2 = "FeII_2328star2"
SRPFeII_2333star = "FeII_2333star"
SRPSiII_2335 = "SiII_2335"
SRPFeII_2338star3 = "FeII_2338star3"
SRPFeII_2344 = "FeII_2344"
SRPFeII_2345star4 = "FeII_2345star4"
SRPFeII_2359star3 = "FeII_2359star3"
SRPFeII_2365star = "FeII_2365star"
SRPFeII_2367 = "FeII_2367"
SRPAlI_2367 = "AlI_2367"
SRPFeII_2374 = "FeII_2374"
SRPFeII_2382 = "FeII_2382"
SRPFeII_2383star = "FeII_2383star"
SRPFeII_2389star = "FeII_2389star"
SRPFeII_2414star4 = "FeII_2414star4"
SRPFeI_2463 = "FeI_2463"
SRPFeI_2484 = "FeI_2484"
SRPFeI_2501 = "FeI_2501"
SRPSiI_2515 = "SiI_2515"
SRPFeI_2523 = "FeI_2523"
SRPMnII_2576 = "MnII_2576"
SRPFeII_2586 = "FeII_2586"
SRPMnII_2594 = "MnII_2594"
SRPFeII_2600 = "FeII_2600"
SRPMnII_2606 = "MnII_2606"
SRPFeII_2607star2 = "FeII_2607star2"
SRPFeII_2618star2 = "FeII_2618star2"
SRPFeII_2621star3 = "FeII_2621star3"
SRPFeII_2622star4 = "FeII_2622star4"
SRPFeII_2626star = "FeII_2626star"
SRPFeII_2629star4 = "FeII_2629star4"
SRPFeI_2719 = "FeI_2719"
SRPMgIIc_2796 = "MgIIc_2796"
SRPMgIIb_2796 = "MgIIb_2796"
SRPMgII_2796 = "MgII_2796"
SRPMgIIa_2796 = "MgIIa_2796"
SRPMgIIc_2803 = "MgIIc_2803"
SRPMgIIb_2803 = "MgIIb_2803"
SRPMgII_2803 = "MgII_2803"
SRPMgIIa_2803 = "MgIIa_2803"
SRPNaI_2852 = "NaI_2852"
SRPMgI_2852 = "MgI_2852"
SRPNaI_2853 = "NaI_2853"
SRPFeI_2967 = "FeI_2967"
SRPFeI_3021 = "FeI_3021"
SRPTiII_3067 = "TiII_3067"
SRPTiII_3073 = "TiII_3073"
SRPAlI_3083 = "AlI_3083"
SRPBeII_3131a = "BeII_3131a"
SRPBeII_3131b = "BeII_3131b"
SRPTiII_3230 = "TiII_3230"
SRPTiII_3242 = "TiII_3242"
SRPNaI_3303a = "NaI_3303a"
SRPNaI_3303b = "NaI_3303b"
SRPTiII_3384 = "TiII_3384"
SRPFeI_3720 = "FeI_3720"
SRPCaII_3934 = "CaII_3934"
SRPAlI_3945 = "AlI_3945"
SRPCaII_3969 = "CaII_3969"
SRPCaI_4227 = "CaI_4227"
SRPHI2_4341 = "HI2_4341"
SRPHI2_4862 = "HI2_4862"
SRPNaI_5891 = "NaI_5891"
SRPNaI_5897 = "NaI_5897"
SRPHI2_6564 = "HI2_6564"


#Transition data
OVII_18 = ( 18.627991, 0.146000, 935000014848.000000) 
OVII_21 = ( 21.601690, 0.696000, 3320000020480.000000) 
HeII_256 = ( 256.316986, 0.079000, 189700000.000000) 
HeII_303 = ( 303.782196, 0.416000, 627000000.000000) 
HeI_515 = ( 515.616516, 0.015400, 200000000.000000) 
HeI_522 = ( 522.212830, 0.030700, 200000000.000000) 
HeI_537 = ( 537.029602, 0.075200, 200000000.000000) 
HeI_584 = ( 584.333984, 0.285000, 200000000.000000) 
MgX_609 = ( 609.789978, 0.084200, 200000000.000000) 
MgX_624 = ( 624.950012, 0.041000, 200000000.000000) 
OIII_702 = ( 702.331970, 0.137000, 200000000.000000) 
NeVIII_770 = ( 770.408997, 0.103000, 100000000.000000) 
NeVIII_780 = ( 780.323975, 0.050500, 100000000.000000) 
OIV_787 = ( 787.710999, 0.110000, 200000000.000000) 
OII_832 = ( 832.757202, 0.044400, 200000000.000000) 
OIII_832 = ( 832.927002, 0.107000, 200000000.000000) 
OII_833 = ( 833.329407, 0.088600, 200000000.000000) 
OII_834 = ( 834.465515, 0.132000, 200000000.000000) 
PIII_913 = ( 913.968018, 0.203100, 4790000128.000000) 
DI_915b = ( 915.080017, 0.000386, 1025000.000000) 
DI_915a = ( 915.575012, 0.000469, 1244000.000000) 
NII_915 = ( 915.612000, 0.144900, 1270000000.000000) 
HI_915 = ( 915.823975, 0.000469, 1243000.000000) 
DI_916b = ( 916.179016, 0.000577, 1531000.000000) 
HI_916 = ( 916.429016, 0.000577, 1529000.000000) 
OI_916b = ( 916.815002, 0.000474, 10000000.000000) 
DI_916a = ( 916.931030, 0.000723, 1913000.000000) 
OI_916a = ( 916.960022, 0.000101, 1330000.000000) 
PIII_917 = ( 917.117981, 0.404900, 4780000256.000000) 
HI_917 = ( 917.180603, 0.000723, 1911000.000000) 
DI_917 = ( 917.879028, 0.000921, 2434000.000000) 
OI_918 = ( 918.044006, 0.000614, 10000000.000000) 
HI_918 = ( 918.129395, 0.000921, 2432000.000000) 
DI_919 = ( 919.101990, 0.001201, 3162000.000000) 
OI_919c = ( 919.221985, 0.000132, 1740000.000000) 
HI_919 = ( 919.351379, 0.001200, 3160000.000000) 
OI_919b = ( 919.658020, 0.000792, 10000000.000000) 
OI_919a = ( 919.916992, 0.000177, 2330000.000000) 
DI_920 = ( 920.711975, 0.001605, 4214000.000000) 
HI_920 = ( 920.963074, 0.001605, 4210000.000000) 
HI_920 = ( 920.963074, 0.001605, 4210000.000000) 
OI_921 = ( 921.856995, 0.001080, 10000000.000000) 
OI_922 = ( 922.200012, 0.000245, 3210000.000000) 
DI_922 = ( 922.898987, 0.002216, 5789000.000000) 
HI_923 = ( 923.150391, 0.002216, 5785000.000000) 
OI_924 = ( 924.950012, 0.001540, 10000000.000000) 
OI_925 = ( 925.445984, 0.000354, 4600000.000000) 
DI_925 = ( 925.973694, 0.003184, 8261000.000000) 
HI_926 = ( 926.225708, 0.003183, 8255000.000000) 
OI_929 = ( 929.516785, 0.002290, 10000000.000000) 
OI_930 = ( 930.256592, 0.000537, 6900000.000000) 
DI_930 = ( 930.495117, 0.004817, 12370000.000000) 
HI_930 = ( 930.748291, 0.004814, 12360000.000000) 
SVI_933 = ( 933.377991, 0.437000, 1670000000.000000) 
OI_936 = ( 936.629517, 0.003650, 17040000.000000) 
DI_937 = ( 937.548401, 0.007808, 24500000.000000) 
HI_937 = ( 937.803528, 0.007799, 24500000.000000) 
OI_937 = ( 937.840515, 0.000877, 11020000.000000) 
SVI_994 = ( 944.523010, 0.215000, 1610000000.000000) 
OI_948 = ( 948.685486, 0.006310, 29000000.000000) 
DI_949 = ( 949.484680, 0.013950, 42040000.000000) 
Ly_d = ( 949.743103, 0.013940, 42040000.000000) 
PIV_950 = ( 950.656921, 1.490000, 3670000128.000000) 
OI_950 = ( 950.884583, 0.001580, 38760000.000000) 
NI_953c = ( 953.414978, 0.013200, 219000000.000000) 
NI_953b = ( 953.655029, 0.025000, 210000000.000000) 
NI_953a = ( 953.969971, 0.034800, 203000000.000000) 
NI_954 = ( 954.104187, 0.004000, 141000000.000000) 
PII_961 = ( 961.041199, 0.348900, 5089999872.000000) 
PII_963 = ( 963.801025, 1.458000, 4140000000.000000) 
NI_963 = ( 963.990295, 0.018370, 85500000.000000) 
NI_964 = ( 964.625610, 0.011800, 83100000.000000) 
NI_965 = ( 965.041321, 0.005801, 81600000.000000) 
OI_971c = ( 971.737122, 0.000138, 1630000.000000) 
OI_971b = ( 971.737610, 0.002070, 14600000.000000) 
OI_971a = ( 971.738220, 0.011600, 85800000.000000) 
DI_972 = ( 972.272217, 0.029010, 81270000.000000) 
Ly_g = ( 972.536804, 0.029000, 81270000.000000) 
OI_976 = ( 976.448120, 0.003310, 80100000.000000) 
CIII_977 = ( 977.020081, 0.757000, 1760000000.000000) 
OI_988c = ( 988.577820, 0.000553, 6290000.000000) 
OI_988b = ( 988.654907, 0.008300, 56600000.000000) 
OI_988a = ( 988.773376, 0.046500, 226000000.000000) 
NIII_989 = ( 989.799011, 0.106600, 500000000.000000) 
NIII_989 = ( 989.799011, 0.106600, 500000000.000000) 
SiII_989 = ( 989.873108, 0.171000, 667299968.000000) 
PIII_997 = ( 997.999573, 0.111700, 2220000000.000000) 
SIII_1012 = ( 1012.494995, 0.043800, 281000000.000000) 
SiII_1020 = ( 1020.698914, 0.016800, 668000000.000000) 
DI_1025 = ( 1025.443359, 0.079100, 189700000.000000) 
Ly_b = ( 1025.722290, 0.079120, 189700000.000000) 
OI_1025 = ( 1025.761597, 0.016300, 102000000.000000) 
MgII_1025 = ( 1025.968140, 0.000743, 2350000.000000) 
MgII_1026 = ( 1026.113403, 0.000392, 2480000.000000) 
OI_1026 = ( 1026.475708, 0.000000, 45800000.000000) 
OVI_1031 = ( 1031.926147, 0.132900, 414900000.000000) 
BeII_1036b = ( 1036.298950, 0.055380, 184600000.000000) 
BeII_1036a = ( 1036.318970, 0.027690, 184600000.000000) 
CII_1036 = ( 1036.336670, 0.118000, 2200000000.000000) 
CIIstar_1037 = ( 1037.018188, 0.118000, 2200000000.000000) 
OVI_1037 = ( 1037.616699, 0.066090, 407600000.000000) 
OI_1039 = ( 1039.230347, 0.009070, 187000000.000000) 
ArI_1048 = ( 1048.219849, 0.263000, 31800000.000000) 
FeII_1055 = ( 1055.261719, 0.006150, 46100000.000000) 
FeII_1062 = ( 1062.151733, 0.002910, 17200000.000000) 
SIV_1062 = ( 1062.663940, 0.049400, 169000000.000000) 
FeII_1063b = ( 1063.176392, 0.054700, 323000000.000000) 
FeII_1063a = ( 1063.971802, 0.004750, 35000000.000000) 
ArI_1066 = ( 1066.659790, 0.067500, 132000000.000000) 
FeII_1081 = ( 1081.874756, 0.012600, 200000000.000000) 
FeII_1083 = ( 1083.420410, 0.002800, 200000000.000000) 
NII_1083 = ( 1083.989990, 0.103100, 374000000.000000) 
FeII_1096 = ( 1096.876953, 0.032700, 226000000.000000) 
FeII_1106 = ( 1106.359619, 0.000394, 2150000.000000) 
FeII_1112 = ( 1112.047974, 0.004460, 20000000.000000) 
PV_1117 = ( 1117.977051, 0.473200, 1260000000.000000) 
FeII_1121 = ( 1121.974854, 0.029000, 192000000.000000) 
FeIII_1122 = ( 1122.524048, 0.054400, 370000000.000000) 
FeII_1125 = ( 1125.447754, 0.015600, 103000000.000000) 
FeII_1127 = ( 1127.098389, 0.001120, 5890000.000000) 
PV_1128 = ( 1128.008057, 0.234500, 1220000000.000000) 
FeII_1133 = ( 1133.665405, 0.004720, 30600000.000000) 
NI_1134c = ( 1134.165283, 0.013420, 151000000.000000) 
NI_1134b = ( 1134.414917, 0.026830, 149000000.000000) 
NI_1134a = ( 1134.980347, 0.040230, 144000000.000000) 
CI_1139 = ( 1139.791870, 0.012300, 21000000.000000) 
FeII_1142 = ( 1142.365601, 0.004010, 25600000.000000) 
FeII_1143 = ( 1143.225952, 0.019200, 98100000.000000) 
FeII_1144 = ( 1144.937866, 0.083000, 352000000.000000) 
PII_1152 = ( 1152.817993, 0.236000, 1230000000.000000) 
CI_1155 = ( 1155.809204, 0.004920, 8190000.000000) 
CI_1157a = ( 1157.329956, 0.001120, 3980000.000000) 
CI_1157b = ( 1157.909668, 0.021200, 35100000.000000) 
MnII_1162 = ( 1162.015015, 0.010200, 39000000.000000) 
CI_1188 = ( 1188.832886, 0.012400, 19500000.000000) 
SIII_1190 = ( 1190.203003, 0.023700, 66500000.000000) 
SiII_1190 = ( 1190.415771, 0.292000, 4080000000.000000) 
CI_1193a = ( 1193.030029, 0.040900, 63900000.000000) 
SiII_1193 = ( 1193.289673, 0.582000, 4070000128.000000) 
CI_1193b = ( 1193.995361, 0.012400, 19400000.000000) 
SiIIstar_1194 = ( 1194.500244, 0.727000, 4080000000.000000) 
MnII_1197 = ( 1197.183960, 0.217000, 784000000.000000) 
SiIIstar_1197 = ( 1197.393799, 0.145000, 4070000128.000000) 
MnII_1199 = ( 1199.390991, 0.169000, 785000000.000000) 
NI_1199 = ( 1199.549561, 0.130000, 407000000.000000) 
NI_1200b = ( 1200.223267, 0.086200, 402000000.000000) 
NI_1200a = ( 1200.709839, 0.043200, 400000000.000000) 
MnII_1201 = ( 1201.118042, 0.121000, 785000000.000000) 
SiIII_1206 = ( 1206.500000, 1.630000, 2480000000.000000) 
FeIII_1214 = ( 1214.562012, 0.000239, 1390000.000000) 
DI_1215 = ( 1215.339355, 0.416500, 627000000.000000) 
Ly_a = ( 1215.670044, 0.416400, 626499968.000000) 
NV_1238 = ( 1238.821045, 0.157000, 339100000.000000) 
MgII_1239 = ( 1239.925293, 0.000632, 1370000.000000) 
MgII_1240 = ( 1240.394653, 0.000356, 1540000.000000) 
NV_1242 = ( 1242.803955, 0.078230, 335600000.000000) 
SII_1250 = ( 1250.578003, 0.005430, 46300000.000000) 
SII_1253 = ( 1253.805054, 0.010900, 46200000.000000) 
SiI_1255 = ( 1255.271973, 0.220100, 310600000.000000) 
SII_1259 = ( 1259.517944, 0.016600, 46500000.000000) 
SiII_1260 = ( 1260.422119, 1.180000, 2950000128.000000) 
FeII_1260 = ( 1260.532959, 0.024000, 126000000.000000) 
CI_1260 = ( 1260.735107, 0.050700, 240000000.000000) 
CIstar_1260a = ( 1260.926147, 0.017500, 241000000.000000) 
CIstar_1260b = ( 1260.996094, 0.013400, 240000000.000000) 
CIstar_1261 = ( 1261.122437, 0.020200, 236000000.000000) 
CIstarstar_1261a = ( 1261.425537, 0.013100, 240000000.000000) 
CIstarstar_1261b = ( 1261.551880, 0.039100, 236000000.000000) 
SiIIstar_1264 = ( 1264.737671, 1.050000, 2929999872.000000) 
SiIIstar_1265 = ( 1265.001953, 0.117000, 2950000128.000000) 
CI_1276 = ( 1276.482178, 0.005890, 8030000.000000) 
CIstar_1276 = ( 1276.749756, 0.003080, 12600000.000000) 
CIstarstar_1277a = ( 1277.189941, 0.000322, 2200000.000000) 
CI_1277 = ( 1277.245239, 0.085300, 232000000.000000) 
CIstar_1277a = ( 1277.282715, 0.066600, 246000000.000000) 
CIstar_1277b = ( 1277.513062, 0.021000, 232000000.000000) 
CIstarstar_1277b = ( 1277.550049, 0.076300, 244000000.000000) 
CIstarstar_1277c = ( 1277.723267, 0.015300, 246000000.000000) 
CIstar_1279 = ( 1279.890747, 0.014300, 117000000.000000) 
CI_1280 = ( 1280.135254, 0.026300, 106000000.000000) 
CIstarstar_1280a = ( 1280.333130, 0.015200, 117000000.000000) 
CIstar_1280a = ( 1280.404297, 0.004400, 106000000.000000) 
CIstar_1280b = ( 1280.597534, 0.007040, 105000000.000000) 
CIstarstar_1280b = ( 1280.847046, 0.005220, 106000000.000000) 
SI_1295 = ( 1295.653076, 0.087000, 346000000.000000) 
TiIII_1295 = ( 1295.884033, 0.041800, 166000000.000000) 
TiIII_1298 = ( 1298.697021, 0.096400, 635000000.000000) 
PII_1301 = ( 1301.874023, 0.017300, 48200000.000000) 
OI_1302 = ( 1302.168457, 0.048000, 565000000.000000) 
SiII_1304 = ( 1304.370239, 0.086300, 1010000000.000000) 
OIstar_1304 = ( 1304.857544, 0.047800, 565000000.000000) 
OIstarstar_1306 = ( 1306.028564, 0.047800, 565000000.000000) 
SiIIstar_1309 = ( 1309.275757, 0.086000, 1010000000.000000) 
NiII_1317 = ( 1317.217041, 0.086000, 420500000.000000) 
CI_1328 = ( 1328.833252, 0.075800, 288000000.000000) 
CIstar_1329a = ( 1329.084961, 0.025400, 289000000.000000) 
CIstar_1329b = ( 1329.100342, 0.031300, 287000000.000000) 
CIstar_1329c = ( 1329.123291, 0.019100, 288000000.000000) 
CIstarstar_1329a = ( 1329.577515, 0.056900, 287000000.000000) 
CIstarstar_1329b = ( 1329.600342, 0.018900, 288000000.000000) 
CII_1334 = ( 1334.532349, 0.127800, 288000000.000000) 
PIII_1334 = ( 1334.813232, 0.028200, 63200000.000000) 
CIIstar_1335b = ( 1335.662720, 0.012770, 288000000.000000) 
CIIstar_1335a = ( 1335.707642, 0.115000, 288000000.000000) 
ClI_1347 = ( 1347.239624, 0.153000, 662000000.000000) 
OI_1335 = ( 1355.597656, 0.000001, 5560.000000) 
CuII_1358 = ( 1358.772949, 0.263000, 720000000.000000) 
BII_1362 = ( 1362.463013, 0.996000, 1190000000.000000) 
CuII_1367 = ( 1367.950928, 0.179000, 623000000.000000) 
NiII_1370 = ( 1370.130981, 0.076900, 410000000.000000) 
NiII_1393 = ( 1393.323975, 0.010100, 34700000.000000) 
SiIV_1393 = ( 1393.760132, 0.513000, 880000000.000000) 
SiIV_1402 = ( 1402.772949, 0.254000, 862000000.000000) 
GaII_1414 = ( 1414.401978, 1.770000, 1970000000.000000) 
CoII_1424 = ( 1424.786621, 0.010900, 35800000.000000) 
NiII_1454 = ( 1454.842041, 0.032300, 102000000.000000) 
CoII_1446 = ( 1466.212036, 0.031000, 37800000.000000) 
NiII_1467b = ( 1467.259033, 0.006300, 29300000.000000) 
NiII_1467a = ( 1467.755981, 0.009900, 23000000.000000) 
SI_1473 = ( 1473.994263, 0.082800, 182000000.000000) 
CoII_1480 = ( 1480.954590, 0.011900, 46500000.000000) 
NiII_1502 = ( 1502.147949, 0.013300, 39320000.000000) 
SiII_1526 = ( 1526.707031, 0.133000, 1130000000.000000) 
PII_1532 = ( 1532.532959, 0.007610, 4770000.000000) 
SiIIstar_1533 = ( 1533.431641, 0.132000, 1130000000.000000) 
CIV_1548 = ( 1548.204102, 0.189900, 264200000.000000) 
CIV_1550 = ( 1550.781250, 0.094750, 262800000.000000) 
CoII_1552 = ( 1552.762451, 0.011600, 32100000.000000) 
CI_1560 = ( 1560.309204, 0.077400, 127000000.000000) 
CIstar_1560a = ( 1560.682007, 0.058100, 127000000.000000) 
CIstar_1560b = ( 1560.708862, 0.019300, 127000000.000000) 
CIstarstar_1561a = ( 1561.339844, 0.011600, 127000000.000000) 
CIstarstar_1561b = ( 1561.366821, 0.000772, 127000000.000000) 
CIstarstar_1561c = ( 1561.437744, 0.064900, 127000000.000000) 
SiI_1562 = ( 1562.001953, 0.375800, 342500000.000000) 
CoII_1572 = ( 1572.648926, 0.012000, 41600000.000000) 
CoII_1574 = ( 1574.550293, 0.025000, 67300000.000000) 
FeII_1588 = ( 1588.687622, 0.000148, 489000.000000) 
ZnI_1589 = ( 1589.561035, 0.121900, 107300000.000000) 
GeII_1602 = ( 1602.486328, 0.134500, 990600000.000000) 
FeII_1608 = ( 1608.450806, 0.057700, 274000000.000000) 
FeII_1611 = ( 1611.200317, 0.001380, 286000000.000000) 
FeII_1618star = ( 1618.468018, 0.034910, 88890000.000000) 
FeII_1621star = ( 1621.685547, 0.060800, 205600000.000000) 
SiI_1625 = ( 1625.705078, 0.068230, 57400000.000000) 
FeII_1629star2 = ( 1629.160034, 0.036700, 205600000.000000) 
SiI_1631 = ( 1631.170044, 0.205100, 171400000.000000) 
FeII_1634star3 = ( 1634.349976, 0.020500, 205600000.000000) 
FeII_1636star3 = ( 1636.331055, 0.040500, 205600000.000000) 
FeII_1639star4 = ( 1639.401001, 0.057900, 205600000.000000) 
HeII_1640 = ( 1640.430054, 0.000000, 0.000000) 
CIstar_1656 = ( 1656.267212, 0.062100, 361000000.000000) 
CI_1656 = ( 1656.928345, 0.149000, 360000000.000000) 
CIstarstar_1657 = ( 1657.008057, 0.111000, 361000000.000000) 
CIstar_1657a = ( 1657.379150, 0.037100, 360000000.000000) 
CIstar_1657b = ( 1657.907104, 0.049400, 360000000.000000) 
CIstarstar_1658 = ( 1658.121094, 0.037100, 361000000.000000) 
AlII_1670 = ( 1670.788574, 1.740000, 1390000000.000000) 
SiI_1693 = ( 1693.293945, 0.156000, 121000000.000000) 
NiII_1703 = ( 1703.405029, 0.006000, 5.000000) 
MgI_1707 = ( 1707.060547, 0.004370, 3330000.000000) 
NiII_1709 = ( 1709.604248, 0.032400, 435000000.000000) 
NiII_1741 = ( 1741.553101, 0.042700, 500000000.000000) 
MgI_1747 = ( 1747.793701, 0.009080, 6610000.000000) 
NiII_1751 = ( 1751.915649, 0.027700, 370000000.000000) 
PI_1774 = ( 1774.948730, 0.169000, 238000000.000000) 
PI_1782 = ( 1782.829102, 0.113000, 238000000.000000) 
SI_1807 = ( 1807.311279, 0.090500, 533000000.000000) 
SiII_1808 = ( 1808.012939, 0.002080, 2380000.000000) 
MgI_1827 = ( 1827.935059, 0.024200, 16100000.000000) 
SiI_1845 = ( 1845.520508, 0.270000, 176000000.000000) 
FeI_1851 = ( 1851.687988, 0.022220, 55580000.000000) 
AlIII_1854 = ( 1854.718262, 0.559000, 542000000.000000) 
AlIII_1862 = ( 1862.791138, 0.278000, 534000000.000000) 
FeII_1901 = ( 1901.772949, 0.000070, 161000.000000) 
TiII_1910b = ( 1910.612305, 0.104000, 417000000.000000) 
TiII_1910a = ( 1910.953857, 0.098000, 143000000.000000) 
CoII_1941 = ( 1941.285156, 0.034000, 435000000.000000) 
CoII_2012 = ( 2012.166382, 0.036790, 345000000.000000) 
ZnII_2026 = ( 2026.137085, 0.501000, 407000000.000000) 
CoII_2026 = ( 2026.412231, 0.012500, 303000000.000000) 
MgI_2026 = ( 2026.476807, 0.113000, 61200000.000000) 
CrII_2056 = ( 2056.256836, 0.103000, 407000000.000000) 
CoII_2059 = ( 2059.475586, 0.007510, 278000000.000000) 
CrII_2062 = ( 2062.236084, 0.075900, 406000000.000000) 
ZnII_2062 = ( 2062.660400, 0.246000, 386000000.000000) 
CrII_2066 = ( 2066.164062, 0.051200, 417000000.000000) 
ZnI_2139 = ( 2139.247314, 1.459000, 709000000.000000) 
FeI_2167 = ( 2167.453369, 0.150000, 274000000.000000) 
FeII_2234 = ( 2234.447266, 0.000025, 275000000.000000) 
FeII_2249 = ( 2249.876709, 0.001821, 331000000.000000) 
FeII_2260 = ( 2260.780518, 0.002440, 258000000.000000) 
AlI_2264 = ( 2264.164795, 0.089200, 71400000.000000) 
CaI_2276 = ( 2276.168945, 0.066100, 28400000.000000) 
NiI_2311 = ( 2311.668945, 0.376500, 470000000.000000) 
NiI_2320 = ( 2320.746826, 0.685000, 694000000.000000) 
FeII_2328star2 = ( 2328.111084, 0.035550, 300000000.000000) 
FeII_2333star = ( 2333.516113, 0.069170, 300000000.000000) 
SiII_2335 = ( 2335.123047, 0.000004, 9610.000000) 
FeII_2338star3 = ( 2338.725098, 0.092500, 300000000.000000) 
FeII_2344 = ( 2344.213867, 0.114200, 268000000.000000) 
FeII_2345star4 = ( 2345.000977, 0.157500, 300000000.000000) 
FeII_2359star3 = ( 2359.827881, 0.057270, 300000000.000000) 
FeII_2365star = ( 2365.552002, 0.049500, 300000000.000000) 
FeII_2367 = ( 2367.590576, 0.000022, 307000000.000000) 
AlI_2367 = ( 2367.774902, 0.106000, 75800000.000000) 
FeII_2374 = ( 2374.461182, 0.031300, 309000000.000000) 
FeII_2382 = ( 2382.765137, 0.320000, 313000000.000000) 
FeII_2383star = ( 2383.788086, 0.005170, 300000000.000000) 
FeII_2389star = ( 2389.357910, 0.082500, 300000000.000000) 
FeII_2414star4 = ( 2414.044922, 0.175500, 300000000.000000) 
FeI_2463 = ( 2463.392090, 0.053200, 500000000.000000) 
FeI_2484 = ( 2484.020996, 0.544000, 500000000.000000) 
FeI_2501 = ( 2501.885742, 0.049300, 385000000.000000) 
SiI_2515 = ( 2515.072510, 0.211000, 222000000.000000) 
FeI_2523 = ( 2523.608398, 0.203000, 385000000.000000) 
MnII_2576 = ( 2576.876953, 0.361000, 282000000.000000) 
FeII_2586 = ( 2586.649658, 0.069125, 272000000.000000) 
MnII_2594 = ( 2594.499023, 0.280000, 278000000.000000) 
FeII_2600 = ( 2600.172852, 0.239400, 270000000.000000) 
MnII_2606 = ( 2606.461914, 0.198000, 272000000.000000) 
FeII_2607star2 = ( 2607.865967, 0.118000, 300000000.000000) 
FeII_2618star2 = ( 2618.398926, 0.050500, 300000000.000000) 
FeII_2621star3 = ( 2621.190918, 0.003920, 300000000.000000) 
FeII_2622star4 = ( 2622.451904, 0.056000, 300000000.000000) 
FeII_2626star = ( 2626.450928, 0.044100, 300000000.000000) 
FeII_2629star4 = ( 2629.077881, 0.173000, 300000000.000000) 
FeI_2719 = ( 2719.833008, 0.122000, 175000000.000000) 
MgIIc_2796 = ( 2796.347412, 0.615500, 262500000.000000) 
MgIIb_2796 = ( 2796.351074, 0.615500, 262500000.000000) 
MgII_2796 = ( 2796.354248, 0.615500, 262500000.000000) 
MgIIa_2796 = ( 2796.355225, 0.615500, 262500000.000000) 
MgIIc_2803 = ( 2803.524414, 0.305800, 259500000.000000) 
MgIIb_2803 = ( 2803.528320, 0.305800, 259500000.000000) 
MgII_2803 = ( 2803.531494, 0.305800, 259500000.000000) 
MgIIa_2803 = ( 2803.532471, 0.305800, 259500000.000000) 
NaI_2852 = ( 2852.811035, 0.001350, 554000.000000) 
MgI_2852 = ( 2852.963135, 1.830000, 500000000.000000) 
NaI_2853 = ( 2853.011963, 0.000677, 554000.000000) 
FeI_2967 = ( 2967.764648, 0.043800, 127000000.000000) 
FeI_3021 = ( 3021.518799, 0.104000, 169000000.000000) 
TiII_3067 = ( 3067.237793, 0.048900, 250000000.000000) 
TiII_3073 = ( 3073.863281, 0.121000, 256000000.000000) 
AlI_3083 = ( 3083.046143, 0.177000, 74500000.000000) 
BeII_3131a = ( 3131.329102, 0.332100, 113000000.000000) 
BeII_3131b = ( 3131.974121, 0.166000, 112900000.000000) 
TiII_3230 = ( 3230.122070, 0.068700, 244000000.000000) 
TiII_3242 = ( 3242.918457, 0.232000, 244000000.000000) 
NaI_3303a = ( 3303.368896, 0.009200, 9641000.000000) 
NaI_3303b = ( 3303.978027, 0.004600, 9639000.000000) 
TiII_3384 = ( 3384.730469, 0.358000, 175000000.000000) 
FeI_3720 = ( 3720.992920, 0.041100, 16300000.000000) 
CaII_3934 = ( 3934.774902, 0.626700, 144400000.000000) 
AlI_3945 = ( 3945.122314, 0.116000, 148000000.000000) 
CaII_3969 = ( 3969.590088, 0.311600, 140900000.000000) 
CaI_4227 = ( 4227.917969, 1.770000, 220000000.000000) 
HI2_4341 = ( 4341.689941, 0.044370, 9425000.000000) 
HI2_4862 = ( 4862.687988, 0.121800, 20620000.000000) 
NaI_5891 = ( 5891.583496, 0.640800, 61570000.000000) 
NaI_5897 = ( 5897.558105, 0.320100, 61390000.000000) 
HI2_6564 = ( 6564.623047, 0.695800, 64650000.000000) 


SRPTransitionDict = {SRPOVII_18:OVII_18, SRPOVII_21:OVII_21, SRPHeII_256:HeII_256, 
    SRPHeII_303:HeII_303, SRPHeI_515:HeI_515, SRPHeI_522:HeI_522, SRPHeI_537:HeI_537, 
    SRPHeI_584:HeI_584, SRPMgX_609:MgX_609, SRPMgX_624:MgX_624, SRPOIII_702:OIII_702, 
    SRPNeVIII_770:NeVIII_770, SRPNeVIII_780:NeVIII_780, SRPOIV_787:OIV_787, SRPOII_832:OII_832, 
    SRPOIII_832:OIII_832, SRPOII_833:OII_833, SRPOII_834:OII_834, SRPPIII_913:PIII_913, 
    SRPDI_915b:DI_915b, SRPDI_915a:DI_915a, SRPNII_915:NII_915, SRPHI_915:HI_915, 
    SRPDI_916b:DI_916b, SRPHI_916:HI_916, SRPOI_916b:OI_916b, SRPDI_916a:DI_916a, SRPOI_916a:OI_916a, 
    SRPPIII_917:PIII_917, SRPHI_917:HI_917, SRPDI_917:DI_917, SRPOI_918:OI_918, SRPHI_918:HI_918, 
    SRPDI_919:DI_919, SRPOI_919c:OI_919c, SRPHI_919:HI_919, SRPOI_919b:OI_919b, SRPOI_919a:OI_919a, 
    SRPDI_920:DI_920, SRPHI_920:HI_920, SRPHI_920:HI_920, SRPOI_921:OI_921, SRPOI_922:OI_922, 
    SRPDI_922:DI_922, SRPHI_923:HI_923, SRPOI_924:OI_924, SRPOI_925:OI_925, SRPDI_925:DI_925, 
    SRPHI_926:HI_926, SRPOI_929:OI_929, SRPOI_930:OI_930, SRPDI_930:DI_930, SRPHI_930:HI_930, 
    SRPSVI_933:SVI_933, SRPOI_936:OI_936, SRPDI_937:DI_937, SRPHI_937:HI_937, SRPOI_937:OI_937, 
    SRPSVI_994:SVI_994, SRPOI_948:OI_948, SRPDI_949:DI_949, SRPLy_d:Ly_d, SRPPIV_950:PIV_950, 
    SRPOI_950:OI_950, SRPNI_953c:NI_953c, SRPNI_953b:NI_953b, SRPNI_953a:NI_953a, SRPNI_954:NI_954, 
    SRPPII_961:PII_961, SRPPII_963:PII_963, SRPNI_963:NI_963, SRPNI_964:NI_964, SRPNI_965:NI_965, 
    SRPOI_971c:OI_971c, SRPOI_971b:OI_971b, SRPOI_971a:OI_971a, SRPDI_972:DI_972, SRPLy_g:Ly_g, 
    SRPOI_976:OI_976, SRPCIII_977:CIII_977, SRPOI_988c:OI_988c, SRPOI_988b:OI_988b, SRPOI_988a:OI_988a, 
    SRPNIII_989:NIII_989, SRPNIII_989:NIII_989, SRPSiII_989:SiII_989, SRPPIII_997:PIII_997, 
    SRPSIII_1012:SIII_1012, SRPSiII_1020:SiII_1020, SRPDI_1025:DI_1025, SRPLy_b:Ly_b, SRPOI_1025:OI_1025, 
    SRPMgII_1025:MgII_1025, SRPMgII_1026:MgII_1026, SRPOI_1026:OI_1026, SRPOVI_1031:OVI_1031, 
    SRPBeII_1036b:BeII_1036b, SRPBeII_1036a:BeII_1036a, SRPCII_1036:CII_1036, SRPCIIstar_1037:CIIstar_1037, 
    SRPOVI_1037:OVI_1037, SRPOI_1039:OI_1039, SRPArI_1048:ArI_1048, SRPFeII_1055:FeII_1055, 
    SRPFeII_1062:FeII_1062, SRPSIV_1062:SIV_1062, SRPFeII_1063b:FeII_1063b, SRPFeII_1063a:FeII_1063a, 
    SRPArI_1066:ArI_1066, SRPFeII_1081:FeII_1081, SRPFeII_1083:FeII_1083, SRPNII_1083:NII_1083, 
    SRPFeII_1096:FeII_1096, SRPFeII_1106:FeII_1106, SRPFeII_1112:FeII_1112, SRPPV_1117:PV_1117, 
    SRPFeII_1121:FeII_1121, SRPFeIII_1122:FeIII_1122, SRPFeII_1125:FeII_1125, SRPFeII_1127:FeII_1127, 
    SRPPV_1128:PV_1128, SRPFeII_1133:FeII_1133, SRPNI_1134c:NI_1134c, SRPNI_1134b:NI_1134b, 
    SRPNI_1134a:NI_1134a, SRPCI_1139:CI_1139, SRPFeII_1142:FeII_1142, SRPFeII_1143:FeII_1143, 
    SRPFeII_1144:FeII_1144, SRPPII_1152:PII_1152, SRPCI_1155:CI_1155, SRPCI_1157a:CI_1157a, 
    SRPCI_1157b:CI_1157b, SRPMnII_1162:MnII_1162, SRPCI_1188:CI_1188, SRPSIII_1190:SIII_1190, 
    SRPSiII_1190:SiII_1190, SRPCI_1193a:CI_1193a, SRPSiII_1193:SiII_1193, SRPCI_1193b:CI_1193b, 
    SRPSiIIstar_1194:SiIIstar_1194, SRPMnII_1197:MnII_1197, SRPSiIIstar_1197:SiIIstar_1197, 
    SRPMnII_1199:MnII_1199, SRPNI_1199:NI_1199, SRPNI_1200b:NI_1200b, SRPNI_1200a:NI_1200a, 
    SRPMnII_1201:MnII_1201, SRPSiIII_1206:SiIII_1206, SRPFeIII_1214:FeIII_1214, SRPDI_1215:DI_1215, 
    SRPLy_a:Ly_a, SRPNV_1238:NV_1238, SRPMgII_1239:MgII_1239, SRPMgII_1240:MgII_1240, SRPNV_1242:NV_1242, 
    SRPSII_1250:SII_1250, SRPSII_1253:SII_1253, SRPSiI_1255:SiI_1255, SRPSII_1259:SII_1259, 
    SRPSiII_1260:SiII_1260, SRPFeII_1260:FeII_1260, SRPCI_1260:CI_1260, SRPCIstar_1260a:CIstar_1260a, 
    SRPCIstar_1260b:CIstar_1260b, SRPCIstar_1261:CIstar_1261, SRPCIstarstar_1261a:CIstarstar_1261a, 
    SRPCIstarstar_1261b:CIstarstar_1261b, SRPSiIIstar_1264:SiIIstar_1264, SRPSiIIstar_1265:SiIIstar_1265, 
    SRPCI_1276:CI_1276, SRPCIstar_1276:CIstar_1276, SRPCIstarstar_1277a:CIstarstar_1277a, 
    SRPCI_1277:CI_1277, SRPCIstar_1277a:CIstar_1277a, SRPCIstar_1277b:CIstar_1277b, 
    SRPCIstarstar_1277b:CIstarstar_1277b, SRPCIstarstar_1277c:CIstarstar_1277c, SRPCIstar_1279:CIstar_1279, 
    SRPCI_1280:CI_1280, SRPCIstarstar_1280a:CIstarstar_1280a, SRPCIstar_1280a:CIstar_1280a, 
    SRPCIstar_1280b:CIstar_1280b, SRPCIstarstar_1280b:CIstarstar_1280b, SRPSI_1295:SI_1295, 
    SRPTiIII_1295:TiIII_1295, SRPTiIII_1298:TiIII_1298, SRPPII_1301:PII_1301, SRPOI_1302:OI_1302, 
    SRPSiII_1304:SiII_1304, SRPOIstar_1304:OIstar_1304, SRPOIstarstar_1306:OIstarstar_1306, 
    SRPSiIIstar_1309:SiIIstar_1309, SRPNiII_1317:NiII_1317, SRPCI_1328:CI_1328, SRPCIstar_1329a:CIstar_1329a, 
    SRPCIstar_1329b:CIstar_1329b, SRPCIstar_1329c:CIstar_1329c, SRPCIstarstar_1329a:CIstarstar_1329a, 
    SRPCIstarstar_1329b:CIstarstar_1329b, SRPCII_1334:CII_1334, SRPPIII_1334:PIII_1334, 
    SRPCIIstar_1335b:CIIstar_1335b, SRPCIIstar_1335a:CIIstar_1335a, SRPClI_1347:ClI_1347,
    SRPOI_1335:OI_1335, SRPCuII_1358:CuII_1358, SRPBII_1362:BII_1362, SRPCuII_1367:CuII_1367, 
    SRPNiII_1370:NiII_1370, SRPNiII_1393:NiII_1393, SRPSiIV_1393:SiIV_1393, SRPSiIV_1402:SiIV_1402, 
    SRPGaII_1414:GaII_1414, SRPCoII_1424:CoII_1424, SRPNiII_1454:NiII_1454, SRPCoII_1446:CoII_1446, 
    SRPNiII_1467b:NiII_1467b, SRPNiII_1467a:NiII_1467a, SRPSI_1473:SI_1473, SRPCoII_1480:CoII_1480, 
    SRPNiII_1502:NiII_1502, SRPSiII_1526:SiII_1526, SRPPII_1532:PII_1532, SRPSiIIstar_1533:SiIIstar_1533, 
    SRPCIV_1548:CIV_1548, SRPCIV_1550:CIV_1550, SRPCoII_1552:CoII_1552, SRPCI_1560:CI_1560, 
    SRPCIstar_1560a:CIstar_1560a, SRPCIstar_1560b:CIstar_1560b, SRPCIstarstar_1561a:CIstarstar_1561a, 
    SRPCIstarstar_1561b:CIstarstar_1561b, SRPCIstarstar_1561c:CIstarstar_1561c, SRPSiI_1562:SiI_1562, 
    SRPCoII_1572:CoII_1572, SRPCoII_1574:CoII_1574, SRPFeII_1588:FeII_1588, SRPZnI_1589:ZnI_1589, 
    SRPGeII_1602:GeII_1602, SRPFeII_1608:FeII_1608, SRPFeII_1611:FeII_1611, SRPFeII_1618star:FeII_1618star, 
    SRPFeII_1621star:FeII_1621star, SRPSiI_1625:SiI_1625, SRPFeII_1629star2:FeII_1629star2, SRPSiI_1631:SiI_1631, 
    SRPFeII_1634star3:FeII_1634star3, SRPFeII_1636star3:FeII_1636star3, SRPFeII_1639star4:FeII_1639star4, 
    SRPHeII_1640:HeII_1640, SRPCIstar_1656:CIstar_1656, SRPCI_1656:CI_1656, SRPCIstarstar_1657:CIstarstar_1657, 
    SRPCIstar_1657a:CIstar_1657a, SRPCIstar_1657b:CIstar_1657b, SRPCIstarstar_1658:CIstarstar_1658, 
    SRPAlII_1670:AlII_1670, SRPSiI_1693:SiI_1693, SRPNiII_1703:NiII_1703, SRPMgI_1707:MgI_1707, 
    SRPNiII_1709:NiII_1709, SRPNiII_1741:NiII_1741, SRPMgI_1747:MgI_1747, SRPNiII_1751:NiII_1751, 
    SRPPI_1774:PI_1774, SRPPI_1782:PI_1782, SRPSI_1807:SI_1807, SRPSiII_1808:SiII_1808, SRPMgI_1827:MgI_1827, 
    SRPSiI_1845:SiI_1845, SRPFeI_1851:FeI_1851, SRPAlIII_1854:AlIII_1854, SRPAlIII_1862:AlIII_1862, 
    SRPFeII_1901:FeII_1901, SRPTiII_1910b:TiII_1910b, SRPTiII_1910a:TiII_1910a, SRPCoII_1941:CoII_1941, 
    SRPCoII_2012:CoII_2012, SRPZnII_2026:ZnII_2026, SRPCoII_2026:CoII_2026, SRPMgI_2026:MgI_2026, 
    SRPCrII_2056:CrII_2056, SRPCoII_2059:CoII_2059, SRPCrII_2062:CrII_2062, SRPZnII_2062:ZnII_2062, 
    SRPCrII_2066:CrII_2066, SRPZnI_2139:ZnI_2139, SRPFeI_2167:FeI_2167, SRPFeII_2234:FeII_2234, 
    SRPFeII_2249:FeII_2249, SRPFeII_2260:FeII_2260, SRPAlI_2264:AlI_2264, SRPCaI_2276:CaI_2276, 
    SRPNiI_2311:NiI_2311, SRPNiI_2320:NiI_2320, SRPFeII_2328star2:FeII_2328star2, SRPFeII_2333star:FeII_2333star, 
    SRPSiII_2335:SiII_2335, SRPFeII_2338star3:FeII_2338star3, SRPFeII_2344:FeII_2344, SRPFeII_2345star4:FeII_2345star4, 
    SRPFeII_2359star3:FeII_2359star3, SRPFeII_2365star:FeII_2365star, SRPFeII_2367:FeII_2367, SRPAlI_2367:AlI_2367, 
    SRPFeII_2374:FeII_2374, SRPFeII_2382:FeII_2382, SRPFeII_2383star:FeII_2383star, SRPFeII_2389star:FeII_2389star, 
    SRPFeII_2414star4:FeII_2414star4, SRPFeI_2463:FeI_2463, SRPFeI_2484:FeI_2484, SRPFeI_2501:FeI_2501, 
    SRPSiI_2515:SiI_2515, SRPFeI_2523:FeI_2523, SRPMnII_2576:MnII_2576, SRPFeII_2586:FeII_2586, 
    SRPMnII_2594:MnII_2594, SRPFeII_2600:FeII_2600, SRPMnII_2606:MnII_2606, SRPFeII_2607star2:FeII_2607star2, 
    SRPFeII_2618star2:FeII_2618star2, SRPFeII_2621star3:FeII_2621star3, SRPFeII_2622star4:FeII_2622star4, 
    SRPFeII_2626star:FeII_2626star, SRPFeII_2629star4:FeII_2629star4, SRPFeI_2719:FeI_2719, 
    SRPMgIIc_2796:MgIIc_2796, SRPMgIIb_2796:MgIIb_2796, SRPMgII_2796:MgII_2796, SRPMgIIa_2796:MgIIa_2796, 
    SRPMgIIc_2803:MgIIc_2803, SRPMgIIb_2803:MgIIb_2803, SRPMgII_2803:MgII_2803, SRPMgIIa_2803:MgIIa_2803, 
    SRPNaI_2852:NaI_2852, SRPMgI_2852:MgI_2852, SRPNaI_2853:NaI_2853, SRPFeI_2967:FeI_2967, SRPFeI_3021:FeI_3021, 
    SRPTiII_3067:TiII_3067, SRPTiII_3073:TiII_3073, SRPAlI_3083:AlI_3083, SRPBeII_3131a:BeII_3131a, 
    SRPBeII_3131b:BeII_3131b, SRPTiII_3230:TiII_3230, SRPTiII_3242:TiII_3242, SRPNaI_3303a:NaI_3303a, 
    SRPNaI_3303b:NaI_3303b, SRPTiII_3384:TiII_3384, SRPFeI_3720:FeI_3720, SRPCaII_3934:CaII_3934, 
    SRPAlI_3945:AlI_3945, SRPCaII_3969:CaII_3969, SRPCaI_4227:CaI_4227, SRPHI2_4341:HI2_4341, 
    SRPHI2_4862:HI2_4862, SRPNaI_5891:NaI_5891, SRPNaI_5897:NaI_5897, SRPHI2_6564:HI2_6564}




