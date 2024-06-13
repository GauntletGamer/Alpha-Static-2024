import openmc, h5py
import numpy as np
import matplotlib.pyplot as plt

def Mean_Lifetime_Plot(SYSTEM="",n=200,k_range=[0.7,1.3]):
    # Defining Variable system critical value, variable multiplier, and unit
    if SYSTEM == "": SYSTEM = input("System ID (G,J,MS): ")
    if SYSTEM == "J":
        Crit_Vals = [6.385,1.280]
        Var_Multi = np.array([0.9,0.93,0.96,1,1.03,1.06,1.1])
        #Var_Multi = np.array([0.7,0.8,0.9,1,1.1,1.2,1.3])
        sys_u = "cm"
    elif SYSTEM == "G":
        Crit_Vals = [8.741,0.995]
        #Var_Multi = np.array([0.9,0.93,0.96,1,1.03,1.06,1.1])
        Var_Multi = np.array([0.7,0.8,0.9,1,1.1,1.2,1.3])
        sys_u = "cm"
    elif SYSTEM == "MS":
        Crit_Vals = [19,3.6]
        Var_Multi = np.array([0.85,0.9,0.95,1,1.05,1.1,1.15])
        sys_u = "%"

    # Defining System Data
    k_Data = np.zeros([2,7])
    kp_Data = np.zeros([2,7])
    kd_Data = np.zeros([2,7])
    ad_Data = np.zeros([2,7])
    ad_Median = np.zeros([2,7])
    ap_Data = np.zeros([2,7])
    ap_Median = np.zeros([2,7])
    Mean_Lifetime = np.zeros([4,7])

    FTB=["Fa","Th"]

    for Fa_Th in FTB:
        if Fa_Th == 'Fa': j = 0
        elif Fa_Th == 'Th': j = 1
        Val_Array = np.round(Var_Multi * Crit_Vals[j],6)
        for i in range(len(Val_Array)):
            Val = Val_Array[i]
            with h5py.File(f"sp.{n}.{Fa_Th}.{Val}{sys_u}.k_eff.delayed.h5","r") as sp:
                k_Data[j,i] = sp['k_combined'][()][0]
            with h5py.File(f"sp.{n}.{Fa_Th}.{Val}{sys_u}.alpha.delayed.h5","r") as sp:
                ad_Data[j,i] = sp['/alpha_mode_tallies/alpha_effective'][()][0]
                ad_Median[j,i] = sp["/alpha_mode_tallies/alpha_median"][()]
                kd_Data[j,i] = sp["/alpha_mode_tallies/k_effective"][()][0]
                Mean_Lifetime[j,i] = sp['alpha_mode_tallies/removal_time'][()][0]
            with h5py.File(f"sp.{n}.{Fa_Th}.{Val}{sys_u}.alpha.prompt.h5","r") as sp:
                ap_Data[j,i] = sp['/alpha_mode_tallies/alpha_effective'][()][0]
                ap_Median[j,i] = sp["/alpha_mode_tallies/alpha_median"][()]
                kp_Data[j,i] = sp["/alpha_mode_tallies/k_effective"][()][0]
                Mean_Lifetime[2+j,i] = sp['alpha_mode_tallies/removal_time'][()][0]
    
    for j in [0,1]:
        c1 = f'C{j}' ; c2 = f'C{j+2}'
        plt.scatter(k_Data[j,:],Mean_Lifetime[j,:],label=f"{FTB[j]},d",c=c1)
        plt.scatter(k_Data[j,:],Mean_Lifetime[j+2,:],label=f"{FTB[j]},p",c=c2)
    plt.title(f"Mean Lifetime for {SYSTEM} vs k-static")
    plt.ylabel("Mean Lifetime (s)")
    plt.xlabel("k-static")
    plt.yscale("log")
    plt.legend()
    plt.grid()
    plt.savefig(f"Mean_Lifetime_{SYSTEM}.png")
    plt.close()

    x = np.linspace(k_range[0],k_range[1],10)
    plt.plot(x,x)
    for j in [0,1]:
        plt.scatter(k_Data[j,:],kp_Data[j,:],label=f"Alpha_P_{FTB[j]}")
        plt.scatter(k_Data[j,:],kd_Data[j,:],label=f"Alpha_D_{FTB[j]}")
    plt.title(f"k-static prompt-only vs k-static delayed for {SYSTEM}")
    plt.legend()
    plt.grid()
    plt.savefig(f"kvk_{SYSTEM}.png")
    plt.close()
Mean_Lifetime_Plot(k_range=[0.9,1.1])