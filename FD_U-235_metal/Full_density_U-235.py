import openmc

# Create Uranium-235 Metal Material
u = openmc.Material()
u.set_density('g/cm3', 19.05)
u.add_nuclide('U235',1)
water = openmc.Material()
water.set_density('g/cm3',1)
water.add_element('H',2)
water.add_element('O',1)
mats = openmc.Materials([u,water])
mats.export_to_xml()

# Create a single sphere cell filled with Uranium Metal
    # Critical Radius: 8.314(Bare) 6.251(Refl)
    # K_eff=0.95 Radius: 7.821(Bare) 5.824(Refl)
    # K_eff=0.98 Radius: 8.115(Bare) 6.077(Refl)
    # 75% CM Radius: 7.554(Bare) 5.679(Refl)
fuel_rad = 5.679
sphere = openmc.Sphere(r=fuel_rad)
reflect_sp = openmc.Sphere(r=fuel_rad+30, boundary_type='vacuum')
cell = openmc.Cell(fill=u, region=-sphere)
cell2 = openmc.Cell(fill=water, region=-reflect_sp & +sphere)
geom = openmc.Geometry([cell,cell2])
geom.export_to_xml()

# Define run settings
settings = openmc.Settings()
settings.batches = 150
settings.inactive = 50
settings.particles = 1000000
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
