import openmc, h5py
import numpy as np
import matplotlib.pyplot as plt

def System_Data_Plot(SYSTEM="",FTB="Fast",n=200,TEXT_FILE=True,k_range=[0.9,1.15]):
    # Defining Variable system critical value, variable multiplier, and unit
    if SYSTEM == "": SYSTEM = input("System ID (G,J,MS): ")
    if SYSTEM == "J":
        Crit_Vals = [6.385,1.280]
        Var_Multi = np.array([0.7,0.8,0.9,1,1.1,1.2,1.3])
        sys_u = "cm"
    elif SYSTEM == "G":
        Crit_Vals = [8.741,0.995]
        Var_Multi = np.array([0.7,0.8,0.9,1,1.1,1.2,1.3])
        sys_u = "cm"
    elif SYSTEM == "MS":
        Crit_Vals = [19,3.6]
        Var_Multi = np.array([0.85,0.9,0.95,1,1.05,1.1,1.15])
        sys_u = "%"
    elif SYSTEM == "MR":        # Replace CUSTOM with 1-2 letter system identifier, also add to System ID input above
        Crit_Vals = [200]              # Fill tuple with critical values as follows: [Fast_val,Thermal_val]
        Var_Multi = np.array([50,100,150,200,250,300,350])    # Fill array with multiplier values, see above for examples
        sys_u = "ratio"                  # Rename string to unit of variation (ex:cm,%)

    # Defining Fast System Data
    k_Data = np.zeros([2,7])
    kp_Data = np.zeros([2,7])
    ad_Data = np.zeros([2,7])
    ad_Median = np.zeros([2,7])
    ap_Data = np.zeros([2,7])
    ap_Median = np.zeros([2,7])
    Mean_Lifetime = np.zeros([4,7])

    if FTB == "Both": FTB=["Fa","Th"]
    elif FTB == "Fast": FTB=["Fa"]
    elif FTB == "Thermal": FTB=["Th"]

    for Fa_Th in FTB:
        if Fa_Th == 'Fa': j = 0
        elif Fa_Th == 'Th': j = 1
        Val_Array = np.round(Var_Multi,6)
        for i in range(len(Val_Array)):
            Val = Val_Array[i]
            with h5py.File(f"sp.{n}.{Fa_Th}.{Val}{sys_u}.k_eff.delayed.h5","r") as sp:
                k_Data[j,i] = sp['k_combined'][()][0]
            with h5py.File(f"sp.{n}.{Fa_Th}.{Val}{sys_u}.alpha.delayed.h5","r") as sp:
                ad_Data[j,i] = sp['/alpha_mode_tallies/alpha_effective'][()][0]
                ad_Median[j,i] = sp["/alpha_mode_tallies/alpha_median"][()]
                Mean_Lifetime[j,i] = sp['alpha_mode_tallies/removal_time'][()][0]
            with h5py.File(f"sp.{n}.{Fa_Th}.{Val}{sys_u}.alpha.prompt.h5","r") as sp:
                ap_Data[j,i] = sp['/alpha_mode_tallies/alpha_effective'][()][0]
                ap_Median[j,i] = sp["/alpha_mode_tallies/alpha_median"][()]
                kp_Data[j,i] = sp["/alpha_mode_tallies/k_effective"][()][0]
                Mean_Lifetime[2+j,i] = sp['alpha_mode_tallies/removal_time'][()][0]

    if any(_=="Fa" for _ in FTB):
        plt.title(r"α vs $k_{eff}$: Graphite System Data")
        plt.scatter(k_Data[0,:],ad_Data[0,:], label=r"$α_{d,eff}$", marker="1",zorder=4)
        plt.scatter(k_Data[0,:],ad_Median[0,:], label=r"$α_{d,med}$", marker="+",zorder=2)
        plt.scatter(k_Data[0,:],ap_Data[0,:], label=r"$α_{p,eff}$", marker="2",zorder=3)
        plt.scatter(k_Data[0,:],ap_Median[0,:], label=r"$α_{p,med}$", marker="+",zorder=1)
        plt.yscale('symlog')
        plt.grid(zorder=0)
        plt.legend()
        plt.savefig("Alpha_vs_K:Graphite.png",dpi=1500)
        plt.close()

    if any(_=="Th" for _ in FTB):
        plt.title(r"α vs $k_{eff}$: Thermal System Data")
        plt.scatter(k_Data[1,:],ad_Data[1,:], label=r"$α_{d,eff}$", marker="1",zorder=4)
        plt.scatter(k_Data[1,:],ad_Median[1,:], label=r"$α_{d,med}$", marker="+",zorder=2)
        plt.scatter(k_Data[1,:],ap_Data[1,:], label=r"$α_{p,eff}$", marker="2",zorder=3)
        plt.scatter(k_Data[1,:],ap_Median[1,:], label=r"$α_{p,med}$", marker="+",zorder=1)
        plt.yscale('symlog')
        plt.grid(zorder=0)
        plt.legend()
        plt.savefig("Alpha_vs_K:Thermal.png",dpi=1500)
        plt.close()

    Reactivity = np.zeros([2,7])
    k_line = np.linspace(k_range[0],k_range[1],100)
    if any(_=="Fa" for _ in FTB):
        Reactivity[0,:] = ap_Data[0,:]*Mean_Lifetime[2,:]/kp_Data[0,:]
        Fa_Coeffs = np.polyfit(k_Data[0,:],Reactivity[0,:],1)
        plt.scatter(k_Data[0,:],Reactivity[0,:],label="Graphite",zorder=3)
        plt.plot(k_line,Fa_Coeffs[0]*k_line+Fa_Coeffs[1],label="Gr: {C[0]:.3f}k{C[1]:.3f}".format(C=Fa_Coeffs))
    if any(_=="Th" for _ in FTB):
        Reactivity[1,:] = ap_Data[1,:]*Mean_Lifetime[3,:]/kp_Data[1,:]
        Th_Coeffs = np.polyfit(k_Data[1,:],Reactivity[1,:],1)
        plt.scatter(k_Data[1,:],Reactivity[1,:],label="Thermal",zorder=2)
        plt.plot(k_line,Th_Coeffs[0]*k_line+Th_Coeffs[1],label="Th: {C[0]:.3f}k{C[1]:.3f}".format(C=Th_Coeffs))
    plt.title(r"$\rho_{\alpha}=\alpha_{p}l/k_{p}$ vs $k_{eff}$")
    plt.grid(zorder=0)
    plt.legend()
    plt.savefig(f"Reactivity_{SYSTEM}.png")
    plt.close()

    plt.title(r"Graphite: Alpha-k vs k-Static")
    plt.scatter(k_Data[0,:],kp_Data[0,:])
    #plt.scatter(k_Data[1,:],kp_Data[1,:])
    plt.plot(k_line,k_line,color="black")
    plt.savefig("alpha-k_vs_static-k.png")


    if TEXT_FILE:
        txt_file = open(f"Reactivity_Data_{SYSTEM}.txt","t+w")
        for i in range(len(Var_Multi)):
            txt_file.write(f"{k_Data[0,i]} {Reactivity[0,i]}\n")
        txt_file.write("\n")
        for i in range(len(Var_Multi)):
            txt_file.write(f"{k_Data[1,i]} {Reactivity[1,i]}\n")
        txt_file.close()

System_Data_Plot(SYSTEM="MR")

####################### NOTES FOR USING #################################
# If you only have one system to run, fill in the necessary information
# in the designated place above (do not delete anything), then when you
# run the function use System_Data_Plot(SYSTEM="(System ID)").
# If you only have Fast or Thermal, then in the function parameters, set
# FTB="Fast" or FTB="Thermal".
# To save the reactivity data for combined analysis (For David's Use) set
# TEXT_FILE=True in the function parameters.
# If you ran your program with more or less than 200 generations, then
# change n=#Gen in parameters.
# To change the desired range for plotting reactivity, change the parameter
# for k_range=[k_min,k_max].
# It's actually important to follow these steps as it makes the compiled
# reactivity plotting process much easier.
# When you finish adding a custom variable system, please save to the cluster.