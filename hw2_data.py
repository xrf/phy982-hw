#!/usr/bin/env python
from numpy import sqrt
from pandas import concat
from common import *

projectile_mass   = 1
projectile_j      = 1/2.
projectile_parity = +1
target        = "Ni60"
target_mass   = 60
target_charge = 28
target_j      = 0
target_parity = +1
J_max         = 50
R_match       = 60

datasets = []

# ----------------------------------------------------------------------------
# proton, 8.2 MeV
# ----------------------------------------------------------------------------

#http://www.nndc.bnl.gov/exfor/servlet/X4sGetReacTabl?reqx=20613&subID=240446003
#DATA-CM     DATA-ERR    EN          ANG-CM      ANG-ERR
#MB/SR       PER-CENT    MEV         ADEG        ADEG
data = parse_table("""
 dcs         dcs_relerr  energy      angle       angle_err
 6590.       3.          8.2         28.7        0.9
 3020.       3.          8.2         32.6        0.9
 1220.       3.          8.2         42.6        0.9
 447.        3.          8.2         52.         0.9
 164.        3.          8.2         62.         0.9
 63.2        3.          8.2         70.8        0.9
 47.7        3.          8.2         80.         0.9
 44.1        3.          8.2         91.         0.9
 48.9        3.          8.2         105.6       0.9
 41.3        3.          8.2         117.3       0.9
 29.7        3.          8.2         124.7       0.9
 20.1        3.          8.2         137.        0.9
 15.5        3.          8.2         145.        0.9
 13.7        3.          8.2         154.7       0.9
 12.6        3.          8.2         164.5       0.9
""")
data["dcs_err"] = data["dcs_relerr"] * data["dcs"] / 100.
data["projectile"] = "p"
datasets.append(data)

# ----------------------------------------------------------------------------
# proton, 55 MeV
# ----------------------------------------------------------------------------

#http://www.nndc.bnl.gov/exfor/servlet/X4sGetReacTabl?reqx=20613&subID=141948002
#DATA-CM     DATA-ERR    EN          EN-ERR      ANG-CM
#MB/SR       MB/SR       MEV         PER-CENT    ADEG
data = parse_table("""
 dcs         dcs_err     energy      energy_err  angle
 30800.      1500.       55.         0.5         5.6
 9880.       490.        55.         0.5         8.1
 3170.       160.        55.         0.5         13.2
 977.        49.         55.         0.5         18.3
 326.        16.         55.         0.5         20.8
 83.5        4.2         55.         0.5         23.4
 51.3        2.6         55.         0.5         25.9
 48.1        2.4         55.         0.5         28.5
 133.        6.6         55.         0.5         33.5
 81.3        4.1         55.         0.5         38.6
 24.3        1.2         55.         0.5         43.7
 12.         0.6         55.         0.5         48.7
 13.1        0.66        55.         0.5         53.8
 11.4        0.57        55.         0.5         58.8
 5.13        0.26        55.         0.5         63.9
 1.85        0.09        55.         0.5         73.9
 1.7         0.09        55.         0.5         78.9
 1.83        0.09        55.         0.5         84.
 2.76        0.14        55.         0.5         99.
 1.63        0.08        55.         0.5         108.9
""")
data["angle_err"] = 0
data["projectile"] = "p"
datasets.append(data)

# ----------------------------------------------------------------------------
# neutron, 5 MeV
# ----------------------------------------------------------------------------

#http://www.nndc.bnl.gov/exfor/servlet/X4sGetReacTabl?reqx=20823&subID=40572003
#DATA        ERR-T       EN          EN-ERR      ANG
#MB/SR       MB/SR       MEV         MEV         ADEG
data = parse_table("""
 dcs         dcs_err     energy      energy_err  angle
 1214.       84.         5.          0.17        20.
 732.        53.         5.          0.17        30.
 397.        24.         5.          0.17        40.
 56.         8.          5.          0.17        55.
 17.         7.          5.          0.17        65.
 21.         6.          5.          0.17        75.
 47.         6.          5.          0.17        90.
 53.         6.          5.          0.17        105.
 34.         6.          5.          0.17        125.
 20.         6.          5.          0.17        135.
 33.         6.          5.          0.17        150.
""")
data["angle_err"] = 0
data["projectile"] = "n"
datasets.append(data)

# ----------------------------------------------------------------------------
# neutron, 24 MeV
# ----------------------------------------------------------------------------

#http://www.nndc.bnl.gov/exfor/servlet/X4sGetReacTabl?reqx=20823&subID=10953004
#DATA        ERR-S       ERR-1       EN          ANG
#MB/SR       PER-CENT    PER-CENT    MEV         ADEG
data = parse_table("""
 dcs         dcs_relrerr dcs_relserr energy      angle
 1102.67     3.          5.          24.         15.
 382.731     3.          5.          24.         20.
 36.939      5.7         5.          24.         25.
 22.28       10.4        5.          24.         30.
 103.966     3.          5.          24.         35.
 137.363     3.          5.          24.         40.
 107.09      3.          5.          24.         45.
 59.733      3.          5.          24.         50.
 30.987      3.          5.          24.         55.
 28.236      3.          5.          24.         60.
 31.352      3.8         5.          24.         65.
 35.749      3.          5.          24.         70.
 29.299      3.3         5.          24.         75.
 20.155      3.          5.          24.         80.
 13.673      3.3         5.          24.         85.
 9.205       5.          5.          24.         90.
 8.294       4.2         5.          24.         95.
 7.489       7.1         5.          24.         100.
 7.698       9.4         5.          24.         105.
 7.223       5.8         5.          24.         110.
 4.397       7.8         5.          24.         120.
 2.645       8.2         5.          24.         130.
 2.049       12.2        5.          24.         140.
 2.771       8.5         5.          24.         150.
""")
data["dcs_err"] = sqrt(data["dcs_relrerr"] ** 2 +
                       data["dcs_relserr"] ** 2) * data["dcs"] / 100.
data["angle_err"] = 0
data["projectile"] = "n"
datasets.append(data)

# ----------------------------------------------------------------------------

data = concat(datasets)
data["origin"] = "expt"
data["target_charge"] = target_charge
data["projectile_charge"] = data["projectile"].map(CHARGE)

maybe_divide_rutherford(data)

# save only the columns we care about
expt_data = data[["origin", "projectile", "energy", "angle", "angle_err",
                  "dcs", "dcs_err", "rdcs", "rdcs_err"]]

# ============================================================================
# optical model parameters
# ============================================================================

#https://www-nds.iaea.org/cgi-bin/ripl_om_param.pl?Z=28&A=60&ID=4100&E1=8.2&E2=8.2
#https://www-nds.iaea.org/cgi-bin/ripl_om_param.pl?Z=28&A=60&ID=4102&E1=55&E2=55
#https://www-nds.iaea.org/cgi-bin/ripl_om_param.pl?Z=28&A=60&ID=401&E1=5&E2=5
#https://www-nds.iaea.org/cgi-bin/ripl_om_param.pl?Z=28&A=60&ID=100&E1=24&E2=24
params = parse_table("""
projectile energy Vvr rvr avr Wvi rvi avi Vsr rsr asr Wsi rsi asi Vor ror aor Woi roi aoi rc
p   8.2   53.5  1.25  0.65    0.0  0.00  0.00    0.0  0.00  0.00   13.5  1.25  0.47    7.5  1.25  0.47    0.0  0.00  0.00   1.25
p  55.0   42.4  1.16  0.75    6.2  1.37  0.37    0.0  0.00  0.00    2.5  1.37  0.37    6.0  1.06  0.78    0.0  0.00  0.00   1.25
n   5.0   45.6  1.29  0.66    0.0  0.00  0.00    0.0  0.00  0.00    9.3  1.25  0.48    7.0  1.29  0.66    0.0  0.00  0.00   0.00
n  24.0   47.0  1.17  0.75    3.7  1.26  0.58    0.0  0.00  0.00    6.2  1.26  0.58    6.2  1.01  0.75    0.0  0.00  0.00   0.00
""")

# ----------------------------------------------------------------------------
