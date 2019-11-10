# AIMS_tools
This library contains a personal collection of scripts to handle AIMS calculations. It's mainly meant for private use or to be shared with students and colleagues. Once it runs efficiently and contains all necessary features, it might also be shared with the AIMS club.

## Currently implemented features:
- **Running AIMS:** prepare_aims.py can set up the files for different tasks (single point, geometry optimisation, band structure calculation, atom-projected density of states)
- **Plotting functionalities:**
The plotting modules are designed for combinatorial plotting with a lot of flexibility. It's very easy to overlay, compare and arrange plots in different fashions with the in-built classes.
    > bandstructure.py can handle band structure plots with scalar relativity, SOC, and mulliken-projection ("fatbands").
        - To do: improve fatband projections, include plotting with spin
    > dos.py handles atom-projected densities of states. Summing up different DOS contributions or to get the total DOS is easily done.
    > multiplots.py contains exemplary functions to combine plots in different fashions, for example overlaying ZORA and ZORA+SOC bandstructures or bandstructures and DOS.
    > To do: instead of making every module in-line executable, I will provide a superscript that automatically detects the calculation type and provides an easy plotting funcitonality.

# Installation
Simply download the zip from github and unpack it. I recommend using a conda environment to handle the package dependencies.
Then run:
> python setup.py install
