# AIMS_tools

This library contains a personal collection of scripts to handle AIMS calculations. It's mainly meant for private use or to be shared with students and colleagues.

## Currently implemented features

- **Handling AIMS calculations:**
    > The installation adds command line tools to your /.local/bin folder which can set up the files for different tasks employing the ASE, sort and analyse results.

    > The **structuretools.py** module contains helper functions to fragment and analyze structures in order to set up different tasks or extract information after a finished calculation.

- **Analyzing results:**
    > The **postprocessing.py** module contains helper functions to extract useful data from finished calculations, such as energies.

    > The **hirshfeld.py** module extracts and evaluates hirshfeld charges.

    > The **eff_mass.py** module can evaluate effective masses in 2 and 3 dimensions.

    > The **phonons.py** module plots phonon spectra from phonopy-FHI aims calculations.

- **Plotting functionalities:**
  
    The plotting modules are designed for flexible, combinatorial plotting. It's very easy to overlay, compare and arrange plots in different fashions with the in-built classes.

    > The **bandstructure.py** module handles band structure plots with scalar relativity, SOC, spin, and mulliken-projection ("fatbands").

    > The **dos.py** module handles atom-projected densities of states.

    > The **multiplots.py** module contains helper functions to combine plots in different fashions, for example overlaying ZORA and ZORA+SOC bandstructures or combining bandstructures and DOS.

## Installation

I recommend using Anaconda to manage package dependencies and updates. See [here](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html).

Simply download the zip from github. Then run:

```bash
pip install AIMS_tools-master.zip
```

Set the path to the aims species (basis sets) in your environment variables (e.g., in the .bashrc):

```bash
export AIMS_SPECIES_DIR="path/to/directory"
```

- On t3000, this one is "/chemsoft/FHI-aims/stable/species_defaults/"
- On taurus, this one is "/projects/m_chemie/FHI-aims/aims_200112/species_defaults/"


## Documentation
The documentation is now available at [ReadTheDocs](aims-tools.readthedocs.io).


## Requirements

- [Atomic Simulation Environment](https://wiki.fysik.dtu.dk/ase/) ase 3.18.1 or higher
- [Space Group Libary](https://atztogo.github.io/spglib/python-spglib.html) spglib
- [Scientific Python](https://www.scipy.org/) scipy (including numpy, matplotlib and pandas)
- [seaborn](https://seaborn.pydata.org/)
- [networkx](https://networkx.github.io/documentation/stable/install.html)

### Other libraries
- [scikit-image](https://scikit-image.org/) for 3D isosurfaces
