import openmc

# Create Plutonium in H2O
pu = openmc.Material(name='Plutonium')
pu.set_density('g/cm3', 19.85)
pu.add_nuclide('Pu239', 1)
water = openmc.Material(name='Water',material_id=3)
water.set_density('g/cm3',1.0)
water.add_element('O',1.0)
water.add_element('H',2.0)
PuWP = 0.03/(0.03+1.0)
PuH2O = openmc.Material.mix_materials([pu,water],[PuWP,1-PuWP],percent_type='wo',name="Pu_H2O_Mix")
mats = openmc.Materials([PuH2O,water])
mats.export_to_xml()

# Create Homogenous Mix Sphere
    # Critical Radius: 16.290
    # K_eff=0.95 Radius: 15.052
    # K_eff=0.98 Radius: 15.770
    # 75% CM Radius: 14.800
fuel_rad = 14.800
sphere = openmc.Sphere(r=fuel_rad)
reflect_sp = openmc.Sphere(r=fuel_rad+30, boundary_type='vacuum')
cell = openmc.Cell(fill=PuH2O, region=-sphere)
cell2 = openmc.Cell(fill=water, region=-reflect_sp & +sphere)
geom = openmc.Geometry([cell,cell2])
geom.export_to_xml()

# Define run settings
settings = openmc.Settings()
settings.batches = 150
settings.inactive = 50
settings.particles = 500000
settings.alpha_mode = True
settings.prompt_only = True
settings.export_to_xml()

# Run Simulation
openmc.run()

# Get resulting k-eff or α-eff value
n = settings.batches
with openmc.StatePoint(f'statepoint.{n}.h5') as sp:
    alpha_eff = sp.alpha_eff
    print(f'Final α-effective = {alpha_eff}')
