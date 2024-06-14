import matplotlib.pyplot as plt
import openmc


# Get results from statepoint
with openmc.StatePoint('statepoint.200.h5') as sp:
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
ax.set_ylabel('Neutron Production')
ax.grid(True, which='both')
plt.savefig('spectrum_problem1_alpha_prompt.png', dpi=600)
#plt.savefig('spectrum.svg')
plt.close()