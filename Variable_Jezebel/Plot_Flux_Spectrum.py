import openmc
import numpy as np
import matplotlib.pyplot as plt

# Get results from statepoint
n = 200
ft = np.array(['Th','Fa'])[0]
R = np.round(np.array([0.7,0.8,0.9,1,1.1,1.2,1.3]) * 6.385,6)[3]
ak = np.array(['alpha','k_eff'])[0]
pd = np.array(['delayed','prompt'])[0]


with openmc.StatePoint('sp.{}.{}.{}cm.{}.{}.h5'.format(n,ft,R,ak,pd)) as sp:
    t = sp.get_tally(name="Flux spectrum")

    # Get the energies from the energy filter
    energy_filter = t.filters[0]
    energies = energy_filter.bins[:, 0]

    # Get the flux values
    mean = t.get_values(value='mean').ravel()
    uncertainty = t.get_values(value='std_dev').ravel()

# Plot flux spectrum
fix, ax = plt.subplots()
ax.loglog(energies, mean, drawstyle='steps-post')
ax.set_xlabel('Energy [eV]')
ax.set_ylabel('Flux')
ax.grid(True, which='both')
plt.savefig("Flux_Plot.{}.{}.{}cm.{}.{}.png".format(n,ft,R,ak,pd))