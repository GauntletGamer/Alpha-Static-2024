import openmc, h5py
import numpy as np

n = 200


for THERMAL in [False]:
    if THERMAL: R_Crit = 200
    else: R_Crit = 200
    for R in np.round(np.array([50,100,150,200,250,300,350]),6):
        for PO in [False,True]:
            if THERMAL: ft = 'Th'
            else: ft = 'Fa'
            ak = 'alpha'
            if PO: pd = 'prompt'
            else: pd = 'delayed'
            with h5py.File('sp.{}.{}.{}ratio.{}.{}.h5'.format(n,ft,R,ak,pd)) as f:
                Mean_Life_Time = f['alpha_mode_tallies/removal_time'][()]
                print(f.filename,Mean_Life_Time)