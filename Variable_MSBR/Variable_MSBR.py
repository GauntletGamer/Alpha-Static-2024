import openmc
import numpy as np
import os
import math
import h5py

def BR(SP_Name):
    with h5py.File(SP_Name) as sp:
        Num_Reacts = sp["/tallies/tally 2/results"][:]
    Num_Fissions = sum(Num_Reacts[0,:4,0])
    Num_Breds = Num_Reacts[0,4,0]
    BR = Num_Breds/Num_Fissions
    return BR

def MSBR_System(BP_index=3,THERMAL=False,k_only=False):
    if THERMAL: Save_to_Txt = open('Thermal_Data.txt','a+t')
    else: Save_to_Txt = open('Fast_Data.txt','a+t')
    B2F = [8.25,4.25]
    Mol_Comp = {"LiF":0.70,"BeF2":0.175,"ThF4":0.125*B2F[0]/sum(B2F),"UF4":0.125*B2F[1]/sum(B2F)}
    enrich = 0.2
    Bred_Crit = [19,3.6][int(THERMAL)] #False=0,True=1
    Bred_Perc = np.round(np.array([0.85,0.9,0.95,1,1.05,1.1,1.15])*Bred_Crit,6)[BP_index] #Base Value of 1.6% in 'actual' system

    salt = openmc.Material(name="salt",temperature=900)
    salt.set_density("g/cc",3.3)
    salt.add_element("F",Mol_Comp['LiF']*1/2+Mol_Comp['BeF2']*2/3+Mol_Comp['UF4']*4/5+Mol_Comp['ThF4']*4/5,'ao')
    salt.add_nuclide("Li7",Mol_Comp['LiF']*1/2,'ao')
    salt.add_element("Be",Mol_Comp['BeF2']*1/3,'ao')
    salt.add_nuclide("U233",Bred_Perc/100*Mol_Comp["ThF4"]*1/5,'ao')
    salt.add_nuclide("U235",enrich*Mol_Comp['UF4']*1/5,'ao')
    salt.add_nuclide("U238",(1-enrich)*Mol_Comp["UF4"]*1/5,'ao')
    salt.add_nuclide("Th232",(1-Bred_Perc/100)*Mol_Comp['ThF4']*1/5,'ao')

    clad = openmc.Material(name="Cladding/Moderator")
    if THERMAL:
        clad.add_element("C",1)
        clad.set_density('g/cm3',2.26)
        clad.add_s_alpha_beta("c_Graphite")
    else:
        clad.set_density('g/cm3', 6.55)
        clad.add_element('Sn', 0.014  , 'wo')
        clad.add_element('Fe', 0.00165, 'wo')
        clad.add_element('Cr', 0.001  , 'wo')
        clad.add_element('Zr', 0.98335, 'wo')

    Mats = openmc.Materials([salt,clad])
    Mats.export_to_xml()

    # Geometry: Cylinder of Salt-Fuel-Mix in Hexagonal Clad/Mod, infinite Hex-Lattice, 2D (inf-z)
    R = 5
    Fuel_Cyl = openmc.ZCylinder(r=R,boundary_type='transmission')
    Mod_Box = openmc.model.HexagonalPrism(7.5,'y',boundary_type='reflective')
    cell1 = openmc.Cell(fill=salt, region=-Fuel_Cyl)
    cell2 = openmc.Cell(fill=clad, region=-Mod_Box & +Fuel_Cyl)
    geometry = openmc.Geometry([cell1,cell2])
    geometry.export_to_xml()

    # Begins the data line with radius
    Save_to_Txt.write(f'\n{Bred_Perc}%')

    # Create Base Settings of Source and Generations
    settings = openmc.Settings()
    settings.particles = 10000
    n = 200
    settings.batches = n
    settings.inactive = 50


    for [AR,PO] in [[False,False],[True,False],[True,True]]:
        settings.alpha_mode = AR
        settings.prompt_only = PO
        settings.export_to_xml()
    
        openmc.run()

        if THERMAL: ft = 'Th'
        else: ft = 'Fa'
        if AR: ak = 'alpha'
        else: ak = 'k_eff'
        if PO: pd = 'prompt'
        else: pd = 'delayed'

        Save_Name = 'sp.{}.{}.{}%.{}.{}.h5'.format(n,ft,Bred_Perc,ak,pd)
        os.rename('statepoint.{}.h5'.format(n),Save_Name)
        with openmc.StatePoint(Save_Name) as sp_file:
            if AR: data = sp_file.alpha_eff
            else: data = sp_file.keff.nominal_value
            Save_to_Txt.write(f" {data}")
            Save_to_Txt.write(f" {BR(Save_Name)}")
        os.rename(Save_Name,"./Statepoint_File/"+Save_Name)
        if k_only == True: break

    Save_to_Txt.close()

# Set up Tallies for Energy Spectrum and Reactions
e_min, e_max = 1e-5, 20.0e6
groups = 500
energies = np.logspace(math.log10(e_min), math.log10(e_max), groups + 1)
energy_filter = openmc.EnergyFilter(energies)

spectrum_tally = openmc.Tally(name="Flux spectrum")
spectrum_tally.filters = [energy_filter]
spectrum_tally.scores = ['flux']

Fission_tally = openmc.Tally(name="Fission Reactions")
Fission_tally.nuclides = ['Th232','U233','U235','U238']
Fission_tally.scores = ['fission','(n,gamma)']

tallies = openmc.Tallies([spectrum_tally,Fission_tally])
tallies.export_to_xml()

# Run the system
#MSBR_System(k_only=True)
#MSBR_System(THERMAL=True,k_only=True)

#for TH in [False,True]:
#    for i in range(7):
#        MSBR_System(BP_index=i,THERMAL=TH)
MSBR_System(BP_index=0)