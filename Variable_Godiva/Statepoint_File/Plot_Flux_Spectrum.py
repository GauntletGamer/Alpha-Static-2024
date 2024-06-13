import openmc
import numpy as np
import matplotlib.pyplot as plt

def SubPlot_Spectrum(ax,sp=openmc.StatePoint,R=None):
    t = sp.get_tally(name="Flux spectrum")

    # Get the energies from the energy filter
    energy_filter = t.filters[0]
    energies = energy_filter.bins[:, 0]
    denergies = energy_filter.bins[:,1]-energies

    # Get the flux values
    mean = t.get_values(value='mean').ravel()
    uncertainty = t.get_values(value='std_dev').ravel()

    # Plot flux spectrum
    
    ax.semilogx(energies, mean*energies/denergies, drawstyle='steps-post',label=f"{R}cm")
    
    
    return ax


def Run_Plot_Spectrum(n=200,Th_Fa=0,i="All",A_K=0,D_P=0,Base_Sys=str(input("Base System J or G: "))):
    # Get results from statepoint
    ft = np.array(['Th','Fa'])[Th_Fa]
    if Base_Sys == "J": R_Crit = np.array([1.280,6.385])
    elif Base_Sys == "G": R_Crit = np.array([0.995,8.741])
    R = np.round(np.array([0.7,0.8,0.9,1,1.1,1.2,1.3]) * R_Crit[Th_Fa],6)
    ak = np.array(['alpha','k_eff'])[A_K]
    pd = np.array(['delayed','prompt'])[D_P]
    fig, ax = plt.subplots()
    if i == "All":
        for i in range(len(R)):
            R_val = R[i]
            with openmc.StatePoint('sp.{}.{}.{}cm.{}.{}.h5'.format(n,ft,R_val,ak,pd)) as sp:
                SubPlot_Spectrum(ax,sp=sp,R=R_val)
        print("Plot Complete: Flux_Plot.{}.{}.{}.{}.png".format(n,ft,ak,pd))
    else:
        R_val = R[i]
        with openmc.StatePoint('sp.{}.{}.{}cm.{}.{}.h5'.format(n,ft,R_val,ak,pd)) as sp:
            SubPlot_Spectrum(ax,sp=sp,R=R_val)
        print("Plot Complete: Flux_Plot.{}.{}.{}cm.{}.{}.png for R={}cm".format(n,ft,R_val,ak,pd))
    
    plt.xlim([1e-5,20e6])
    [Mean_Min,Mean_Max] = plt.ylim()
    plt.ylim([0,Mean_Max])
    ax.grid(True, which='both')
    ax.set_xlabel('Energy [eV]')
    ax.set_ylabel(r'$E\Phi(E)$')
    if Th_Fa == 0:
        plt.title(r"Thermal System: $E\Phi(E)$ vs E (eV)")
    elif Th_Fa == 1:
        plt.title(r"Fast System: $E\Phi(E)$ vs E (eV)")    
    plt.legend()
    if i == "All": plt.savefig("Flux_Plot.{}.{}.{}.{}.png".format(n,ft,ak,pd))
    else: plt.savefig("Flux_Plot.{}.{}.{}cm.{}.{}.png".format(n,ft,R_val,ak,pd))
        

Run_Plot_Spectrum()
Run_Plot_Spectrum(Th_Fa=1)