import openmc, h5py
import numpy as np
import matplotlib.pyplot as plt

# Defining Fast System Data
k_Data = np.zeros([2,7])
kp_Data = np.zeros([2,7])
ad_Data = np.zeros([2,7])
ad_Median = np.zeros([2,7])
ap_Data = np.zeros([2,7])
ap_Median = np.zeros([2,7])
Mean_Removal = np.zeros([4,7])
STD = np.zeros([6,7])

n = 200
for Fa_Th in ['Fa','Th']:
    if Fa_Th == 'Fa': BP_Crit = 19 ; j = 0
    elif Fa_Th == 'Th': BP_Crit = 3.6 ; j = 1
    BP_Array = np.round(np.array([0.85,0.9,0.95,1,1.05,1.1,1.15]) * BP_Crit,6)
    for i in range(7):
        R = BP_Array[i]
        with h5py.File(f"sp.{n}.{Fa_Th}.{R}%.k_eff.delayed.h5","r") as sp:
            k_Data[j,i] = sp['k_combined'][()][0]
            STD[j,i] = sp['k_combined'][()][1]
        with h5py.File(f"sp.{n}.{Fa_Th}.{R}%.alpha.delayed.h5","r") as sp:
            ad_Data[j,i] = sp['/alpha_mode_tallies/alpha_effective'][()][0]
            ad_Median[j,i] = sp["/alpha_mode_tallies/alpha_median"][()]
            Mean_Removal[j,i] = sp['alpha_mode_tallies/removal_time'][()][0]
            STD[j+2,i] = sp['/alpha_mode_tallies/alpha_effective'][()][1]
        with h5py.File(f"sp.{n}.{Fa_Th}.{R}%.alpha.prompt.h5","r") as sp:
            ap_Data[j,i] = sp['/alpha_mode_tallies/alpha_effective'][()][0]
            ap_Median[j,i] = sp["/alpha_mode_tallies/alpha_median"][()]
            Mean_Removal[2+j,i] = sp['alpha_mode_tallies/removal_time'][()][0]
            kp_Data[j,i] = sp["/alpha_mode_tallies/k_effective"][()][0]
            STD[j+4,i] = sp['/alpha_mode_tallies/alpha_effective'][()][1]


plt.title(r"α vs $k_{eff}$: Fast System Data")
plt.scatter(k_Data[0,:],ad_Data[0,:], label=r"$α_{d,eff}$", marker="1",zorder=4,)
#plt.errorbar(k_Data[0,:],ad_Data[0,:],xerr=STD[0,:],yerr=STD[2,:])
plt.scatter(k_Data[0,:],ad_Median[0,:], label=r"$α_{d,med}$", marker="+",zorder=2)
plt.scatter(k_Data[0,:],ap_Data[0,:], label=r"$α_{p,eff}$", marker="2",zorder=3)
#plt.errorbar(k_Data[0,:],ap_Data[0,:],xerr=STD[0,:],yerr=STD[4,:])
plt.scatter(k_Data[0,:],ap_Median[0,:], label=r"$α_{p,med}$", marker="+",zorder=1)
plt.yscale('symlog')
plt.grid(zorder=0)
plt.legend()
plt.savefig("Variable_BP_Fast.png",dpi=1500)
plt.close()

plt.title(r"α vs $k_{eff}$: Thermal System Data")
plt.scatter(k_Data[1,:],ad_Data[1,:], label=r"$α_{d,eff}$", marker="1",zorder=4)
#plt.errorbar(k_Data[1,:],ad_Data[1,:],xerr=STD[1,:],yerr=STD[3,:])
plt.scatter(k_Data[1,:],ad_Median[1,:], label=r"$α_{d,med}$", marker="+",zorder=2)
plt.scatter(k_Data[1,:],ap_Data[1,:], label=r"$α_{p,eff}$", marker="2",zorder=3)
#plt.errorbar(k_Data[1,:],ap_Data[1,:],xerr=STD[1,:],yerr=STD[5,:])
plt.scatter(k_Data[1,:],ap_Median[1,:], label=r"$α_{p,med}$", marker="+",zorder=1)
plt.yscale('symlog')
plt.grid(zorder=0)
plt.legend()
plt.savefig("Variable_BP_Thermal.png",dpi=1500)
plt.close()

Reactivity = np.zeros([2,7])
Reactivity[0,:] = ap_Data[0,:]*Mean_Removal[2,:]/kp_Data[0,:]
Reactivity[1,:] = ap_Data[1,:]*Mean_Removal[3,:]/kp_Data[1,:]
#print(ReactivityK)
plt.title(r"$\rho_{\alpha}=\alpha_{p}l/k_p$ vs $k_{eff}$")
plt.scatter(k_Data[0,:],Reactivity[0,:],label="Fast",zorder=3)
plt.scatter(k_Data[1,:],Reactivity[1,:],label="Thermal",zorder=2)
Fa_Coeffs = np.polyfit(k_Data[0,:],Reactivity[0,:],1)
Th_Coeffs = np.polyfit(k_Data[1,:],Reactivity[1,:],1)
k_line = np.linspace(0.9,1.1,1000)
plt.plot(k_line,Fa_Coeffs[0]*k_line+Fa_Coeffs[1],label="Fa: {C[0]:.3f}k{C[1]:.3f}".format(C=Fa_Coeffs))
plt.plot(k_line,Th_Coeffs[0]*k_line+Th_Coeffs[1],label="Th: {C[0]:.3f}k{C[1]:.3f}".format(C=Th_Coeffs))
plt.grid(zorder=0)
plt.legend()
plt.savefig("Reactivity.png")
plt.close()