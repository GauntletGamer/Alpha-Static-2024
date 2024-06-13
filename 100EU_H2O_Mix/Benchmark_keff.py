import openmc
import openmc.model
import numpy as np
import matplotlib.pyplot as plt

mats = openmc.Materials.from_xml(path='materials.xml')
fuel = mats[0]
water = mats[1]
print(fuel)
print(water)
def build_model(radius):
    # Create a single cell filled with the Pu metal
    sphere = openmc.Sphere(r=radius)
    reflect_sph = openmc.Sphere(r=radius+30, boundary_type='vacuum')
    cell = openmc.Cell(fill=fuel, region=-sphere)
    cell2 = openmc.Cell(fill=water, region=-reflect_sph & +sphere)
    geom = openmc.Geometry([cell,cell2])

    # Define run settings
    setts = openmc.Settings()
    setts.batches = 150
    setts.inactive = 50
    setts.particles = 10000
    setts.output = {'tallies': False}

    model = openmc.model.Model(geometry=geom,materials=mats,settings=setts)

    return model

Target_keff = float(input("Input Desired keff: "))

Conv_r, guesses, keffs = openmc.search_for_keff(build_model,bracket=[10,20],target=Target_keff,tol=1e-5,print_iterations=True,run_args={'output':False})

print(Conv_r)
print(guesses)

plt.scatter(guesses,[keffs[i].nominal_value for i in range(len(keffs))])
plt.scatter(Conv_r,Target_keff)
plt.savefig("Radius_Convergence_{}.png".format(Target_keff))

for i in range(len(guesses)):
    print("{}\t{}".format(guesses[i],keffs[i].nominal_value))
