import openmc

# Create Full Density Pu-239 Materials
pu = openmc.Material()
pu.set_density('g/cm3',19.85)
pu.add_nuclide('Pu239',1)
water = openmc.Material()
water.set_density('g/cm3',1)
water.add_element('H',2)
water.add_element('O',1)
#water.add_s_alpha_beta('c_H_in_H2O')
mats = openmc.Materials([pu,water])
mats.export_to_xml()

# Create a Pu sphere surounded by water
    # Critical Radius: 4.932(Bare) 3.960(refl)
    # K_eff=0.95 Radius: 4.648(Bare) 3.719(refl)
    # K_eff=0.98 Radius: 4.814(Bare) 3.861(refl)
    # 75% CM Radius: 4.481(Bare)  3.598(refl)
fuel_rad = 3.960
sphere = openmc.Sphere(r=fuel_rad)
reflect_sp = openmc.Sphere(r=fuel_rad+30, boundary_type='vacuum')
cell = openmc.Cell(fill=pu, region=-sphere)
cell2 = openmc.Cell(fill=water, region=-reflect_sp & +sphere)
geom = openmc.Geometry([cell,cell2])
geom.export_to_xml()

# Define run settings
settings = openmc.Settings()
settings.batches = 150
settings.inactive = 50
settings.particles = 1000000
#settings.alpha_mode = True
#settings.prompt_only = True
settings.export_to_xml()

# Run Simulation
openmc.run()

# Get resulting k-eff or α-eff value
n = settings.batches
with openmc.StatePoint(f'statepoint.{n}.h5') as sp:
    alpha_eff = sp.alpha_eff
    print(f'Final α-effective = {alpha_eff}')
