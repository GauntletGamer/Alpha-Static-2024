import openmc
import numpy as np
import os
import math

def Run_System(R_index=3,THERMAL=False):
    if THERMAL: Save_to_Txt = open('Thermal_Data.txt','a+t')
    else: Save_to_Txt = open('Fast_Data.txt','a+t')

    # Material Composition of the Jezebel Sphere
    fuel = openmc.Material(name="Fuel",material_id=1)
    fuel.set_density('sum')
    fuel.add_nuclide('Pu239', 3.7047e-02)
    fuel.add_nuclide('Pu240', 1.7512e-03)
    fuel.add_nuclide('Pu241', 1.1674e-04)
    fuel.add_element('Ga', 1.3752e-03)
    # If System is thermal, moderator (Water) is added
    if THERMAL:
        mod = openmc.Material(name="Moderator",material_id=2)
        mod.set_density('g/cm3',1.0)
        mod.add_element('H',2.0)
        mod.add_element('O',1.0)
        fuel_mod = openmc.Material.mix_materials([fuel,mod],[1/1001,1000/1001],'ao')
        fuel_mod.add_s_alpha_beta('c_H_in_H2O',1)
        fuel_mod.set_density('g/cm3',fuel.get_mass_density())
        materials = openmc.Materials([fuel_mod])
    else:
        materials = openmc.Materials([fuel])
    materials.export_to_xml()

    # 7 Radius values around the Jezebel radius = 6.3849
    if THERMAL: R_Crit = 1.280
    else: R_Crit = 6.385
    R_Array = np.round(np.array([0.9,0.93,0.96,1,1.03,1.06,1.1]) * R_Crit,6)
    R = R_Array[R_index]
    Fuel_Sphere = openmc.Sphere(r=R,boundary_type='vacuum')
    if THERMAL:
        cell1 =openmc.Cell(fill=fuel_mod,region=-Fuel_Sphere)
    else: 
        cell1 = openmc.Cell(fill=fuel,region=-Fuel_Sphere)
    geometry = openmc.Geometry([cell1])
    geometry.export_to_xml()

    # Begins the data line with radius
    Save_to_Txt.write(f'\n{R}')

    # Create Base Settings of Source and Generations
    settings = openmc.Settings()
    settings.particles = 100000
    n = 200
    settings.batches = n
    settings.inactive = 50

    # Saving Flux Tallies to produce energy spectrum
    e_min, e_max = 1e-5, 20.0e6
    groups = 500
    energies = np.logspace(math.log10(e_min), math.log10(e_max), groups + 1)
    energy_filter = openmc.EnergyFilter(energies)

    spectrum_tally = openmc.Tally(name="Flux spectrum")
    spectrum_tally.filters = [energy_filter]
    spectrum_tally.scores = ['flux']

    tallies = openmc.Tallies([spectrum_tally])
    tallies.export_to_xml()

    for AR in [False,True]:
        settings.alpha_mode = AR
        for PO in [False,True]:
            settings.prompt_only = PO
            settings.export_to_xml()
            
            if not ((AR == False) and (PO)):
                openmc.run()

                if THERMAL: ft = 'Th'
                else: ft = 'Fa'
                if AR: ak = 'alpha'
                else: ak = 'k_eff'
                if PO: pd = 'prompt'
                else: pd = 'delayed'

                os.rename('statepoint.{}.h5'.format(n),'sp.{}.{}.{}cm.{}.{}.h5'.format(n,ft,R,ak,pd))
                with openmc.StatePoint('sp.{}.{}.{}cm.{}.{}.h5'.format(n,ft,R,ak,pd)) as sp_file:
                    if AR: data = sp_file.alpha_eff
                    else: data = sp_file.keff.nominal_value
                    Save_to_Txt.write(f" {data}")

    Save_to_Txt.close()


for THERMAL in [False,True]:  
    for i in range(7):
        Run_System(R_index=i,THERMAL=THERMAL)
