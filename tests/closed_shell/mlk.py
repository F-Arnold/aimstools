import numpy as np
import re
import matplotlib.pyplot as plt
from AIMS_tools import BandStructure

bs  = BandStructure(".")
bs.get_properties()
bs.plot()
#s = bs.spectrum.get_species_contribution("B")
#bs.plot_all_species(window=5, mode="lines", bandpath="GXMGMXG")
#con1 = bs.spectrum.get_species_contribution("Fe")
#con2 = bs.spectrum.get_species_contribution("S")
#bs.plot_segmented([con1, con2])
