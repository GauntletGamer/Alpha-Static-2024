import openmc, h5py
import matplotlib.pyplot as plt
import numpy as np

NUM_GEN = int(input("Statepoint File #: "))

with h5py.File(f"statepoint.{NUM_GEN}.h5","r") as f:
    k_generation = f['k_generation'][()]
    alpha_generation = f['alpha_mode_tallies/alpha_generation'][()]
    k_eff = f['alpha_mode_tallies/k_effective'][()][0]
    alpha_eff = f['alpha_mode_tallies/alpha_effective'][()][0]
    alpha_median = f['alpha_mode_tallies/alpha_median'][()]
    n_inactive = f['n_inactive'][()]
    n_total = f['n_batches'][()]
    N_Particles = f['n_particles'][()]
#print(k_generation)
#print(alpha_generation)
print("Particles:\t",N_Particles)
print("Total Batches:\t",n_total)
print("Inact Batches:\t",n_inactive)
print("Effective k:\t",k_eff)
print("Effective a:\t",alpha_eff)
print("Median a:\t",alpha_median)


fig, ax = plt.subplots(2,1)
fig.suptitle(f"k and a Generation for {N_Particles} Neutrons")
ax[0].plot(np.arange(n_inactive,n_total),k_generation[n_inactive:])
ax[0].hlines(k_eff,n_inactive,n_total,linestyles="--",colors='orange')
ax[0].set_ylabel('K_Generation')


ax[1].plot(np.arange(n_inactive,n_total),alpha_generation[n_inactive:])
ax[1].hlines([alpha_eff,alpha_median],n_inactive,n_total,linestyles='--',colors=['orange','red'])
ax[1].set_yscale('symlog')
ax[1].set_ylabel('Alpha_Generation')
fig.savefig('Gen_{}.png'.format(N_Particles),dpi=1500)


N_bins = 50
min_lambda = 0.0128
Shifted_alpha_generation = alpha_generation[:] + min_lambda #temporary value
Shifted_mean = alpha_eff + min_lambda
Shifted_median = alpha_median + min_lambda
fig2, ax2 = plt.subplots(1,1)
fig2.suptitle(f"a Generation groups")
ax2.hist(Shifted_alpha_generation,bins=np.logspace(-4,np.log10(np.max(Shifted_alpha_generation)),N_bins))
ax2.vlines([Shifted_mean,Shifted_median,min_lambda],0,10,linestyles='--',colors=['orange','red','green'])
ax2.set_xscale('log')
fig2.savefig("Alpha_Histogram_{}.png".format(N_Particles),dpi=1500)
