import openmc
import h5py


with h5py.File("sp.200.Fa.19.0%.k_eff.delayed.h5") as sp:
    for nuc in sp["/tallies/tally 2/nuclides"]:
        print(str(nuc))
    for bin in sp["/tallies/tally 2/score_bins"]:
        print(str(bin))
    Num_Reacts = sp["/tallies/tally 2/results"][:]
print(Num_Reacts)
print(Num_Reacts.shape)
print(Num_Reacts[0,:,0])
Num_Fissions = sum(Num_Reacts[0,:4,0])
Num_Breds = sum(Num_Reacts[0,[4,7],0])
BR = Num_Breds/Num_Fissions
print(BR)