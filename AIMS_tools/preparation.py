import ase.io, ase.cell
from ase import Atoms
from ase.calculators.aims import Aims

import argparse

from AIMS_tools.misc import *
from AIMS_tools.structuretools import structure


class prepare:
    """ A base class to initialise and prepare AIMS calculations.
    
    Args:
        geometry (str): Path to geometry file.

    Keyword Arguments:
        xc (str): Exchange-Correlation functional. Defaults to pbe.
        spin (str): None or collinear. Defaults to None.
        basis (str): Basis set quality. Defaults to tight.
        tier (int): Basis set tier. Defaults to 2.
        k_grid (list): List of integers for k-point sampling. Defaults to [6,6,6].
        task (list): List of tasks to perform. Defaults to []. Currently available: BS, DOS, GO, fatBS, phonons.

    Other Parameters:        
        cluster (str): HPC cluster. Defaults to taurus.
        cost (str): low, medium or high. Automatically adjusts nodes and walltimes depending on the cluster.        
    """

    def __init__(self, geometryfile, *args, **kwargs):
        # Arguments
        self.path = Path(geometryfile).parent
        self.cluster = kwargs.get("cluster", "taurus")
        self.cost = kwargs.get("cost", "low")
        self.xc = kwargs.get("xc", "pbe")
        self.spin = kwargs.get("spin", None)
        self.tier = kwargs.get("tier", 2)
        self.basis = kwargs.get("basis", "tight")
        self.k_grid = kwargs.get("k_grid", [6, 6, 6])
        self.task = kwargs.get("task", [])
        # Initialisation
        try:
            self.species_dir = os.getenv("AIMS_SPECIES_DIR")
            assert self.species_dir != None, "Basis sets not found!"
        except:
            logging.critical("Basis sets not found!")
        cwd = Path.cwd()
        self.species_dir = str(cwd.joinpath(Path(self.species_dir, self.basis)))
        self.structure = structure(geometryfile)
        self.name = (
            str(Path(geometryfile).parts[-1]).split(".")[0]
            if str(geometryfile) != "geometry.in"
            else self.structure.atoms.get_chemical_formula()
        )
        if self.structure.is_2d(self.structure.atoms) == True:
            self.k_grid = [self.k_grid[0], self.k_grid[1], 1]
            logging.info("Structure is treated as 2D.")
            try:
                self.structure.atoms = self.structure.enforce_2d()
            except:
                logging.warning("2D could not be enforced.")

    def setup_calculator(self):
        """ This function sets up the calculator object of the ASE.
        Because certain functions are not implemented yet, it simply
        writes out the input files."""
        cwd = Path.cwd()
        os.chdir(self.path)
        calc = Aims(
            xc=self.xc,
            spin=self.spin,
            species_dir=self.species_dir,
            tier=self.tier,
            k_grid=self.k_grid,
            relativistic=("atomic_zora", "scalar"),
            adjust_scf="always 3",
        )
        self.structure.atoms.set_calculator(calc)
        calc.prepare_input_files()
        os.chdir(cwd)

    def setup_bandpath(self):
        """ This function sets up the band path according to AFLOW conventions.
  
        Returns:
            list: List of strings containing the k-path sections.
        """
        from ase.dft.kpoints import parse_path_string

        atoms = self.structure.atoms
        if self.structure.is_2d(atoms) == True:
            atoms.pbc = [True, True, False]
        path = parse_path_string(
            atoms.cell.get_bravais_lattice(pbc=atoms.pbc).bandpath().path
        )
        # list Of lists of path segments
        points = atoms.cell.get_bravais_lattice(pbc=atoms.pbc).bandpath().special_points
        segments = []
        npoints = 31
        for seg in path:
            section = [(i, j) for i, j in zip(seg[:-1], seg[1:])]
            segments.append(section)
        output_bands = []
        index = 1
        for seg in segments:
            output_bands.append("## Brillouin Zone section Nr. {:d}\n".format(index))
            for sec in seg:
                vec1 = "{:.6f} {:.6f} {:.6f}".format(*points[sec[0]])
                vec2 = "{:.6f} {:.6f} {:.6f}".format(*points[sec[1]])
                output_bands.append(
                    "{vec1} \t {vec2} \t {npoints} \t {label1} {label2}".format(
                        label1=sec[0],
                        label2=sec[1],
                        npoints=npoints,
                        vec1=vec1,
                        vec2=vec2,
                    )
                )
            index += 1
        return output_bands

    def setup_symmetries(self):
        """ This function sets up symmetry constraints for lattice relaxation.
        
        Returns:
            str : Symmetry block to be added in geometry.in.
        """
        atoms = self.structure.atoms
        try:
            self.structure.standardize()
            assert len(self.structure.atoms) == len(
                atoms
            ), "Number of atoms changed due to standardization."
        except:
            self.structure.atoms = atoms
            atoms.set_cell(atoms.cell.standard_form()[0])
        lat = self.structure.lattice
        if lat == "triclinic":
            nlat = 9
            sym_params = "symmetry_params a1 a2 a3 b1 b2 b3 c1 c2 c3"
            latstring = "symmetry_lv a1 , a2 , a3 \nsymmetry_lv b1 , b2 , b3 \nsymmetry_lv c1 , c2 , c3\n"
        elif lat == "monoclinic":
            # a != b != c, alpha = gamma != beta
            nlat = 4
            sym_params = "symmetry_params a1 b2 c2 c3"
            latstring = "symmetry_lv a1 , 0 , 0 \nsymmetry_lv 0 , b2 , 0 \nsymmetry_lv 0 , c2 , c3\n"
        elif lat == "orthorhombic":
            # a != b != c, alpha = beta = gamma = 90
            nlat = 3
            sym_params = "symmetry_params a1 b2 c3"
            latstring = "symmetry_lv a1 , 0 , 0 \nsymmetry_lv 0 , b2 , 0 \nsymmetry_lv 0 , 0 , c3\n"
        elif lat == "tetragonal":
            # a = b != c, alpha = beta = gamma = 90
            nlat = 2
            sym_params = "symmetry_params a1 c3"
            latstring = "symmetry_lv a1 , 0 , 0 \nsymmetry_lv 0 , a1 , 0 \nsymmetry_lv 0 , 0 , c3\n"
        elif (lat == "trigonal") or (lat == "hexagonal"):
            # a = b != c, alpha = beta = 90, gamma = 120
            nlat = 2
            sym_params = "symmetry_params a1 c3"
            latstring = "symmetry_lv a1 , 0 , 0 \nsymmetry_lv -a1/2 , sqrt(3.0)*a1/2 , 0 \nsymmetry_lv 0 , 0 , c3\n"
        elif lat == "cubic":
            # a = b = c, alpha = beta = gamma = 90
            nlat = 1
            sym_params = "symmetry_params a1"
            latstring = "symmetry_lv a1 , 0 , 0 \nsymmetry_lv 0 , a1 , 0 \nsymmetry_lv 0 , 0 , a1\n"
        nparams = "symmetry_n_params {} {} {}\n".format(
            nlat + len(atoms) * 3, nlat, len(atoms) * 3
        )
        sym_frac = ""
        for i in range(len(atoms) * 3):
            sym_params += " x{}".format(i)
            if (i % 3) == 0:
                sym_frac += "symmetry_frac x{} , x{} , x{}\n".format(i, i + 1, i + 2)
        logging.warning(
            "I'm not sure yet the symmetry block is correct for every setting and handedness. Take care!"
        )
        return nparams + sym_params + "\n" + latstring + sym_frac

    def __adjust_xc(self, line):
        if "hse06" in line:
            line = "xc                                 hse06 0.11\n"
            line += "hse_unit        bohr-1\n"
            line += "exx_band_structure_version        1\n"

        line += "# include_spin_orbit\n"
        line += "# Common choices of dispersion methods:\n"
        line += "# \t vdw_correction_hirshfeld\n"
        line += "# \t many_body_dispersion\n"
        line += "# \t many_body_dispersion_nl \t beta=0.81\n"
        return line

    def __adjust_scf(self, line):
        line = "### SCF settings \n"
        line += "adjust_scf \t always \t 3 \n"
        line += "# frozen_core_scf \t .true. \n"
        line += "# charge_mix_param  0.05\n"
        line += "# occupation_type \t gaussian \t 0.01 \n"
        line += "# sc_accuracy_eev   1E-3 \t \t # sum of eigenvalues convergence\n"
        line += "# sc_accuracy_etot  1E-6 \t \t # total energy convergence\n"
        line += "# sc_accuracy_rho   1E-3 \t \t # electron density convergence\n"
        line += "# elsi_restart \t read_and_write \t 1000\n"
        return line

    def __adjust_task(self, line):
        if "BS" in self.task:
            output_bands = self.setup_bandpath()
            line += "### band structure section \n"
            for band in output_bands:
                if not band.startswith("#"):
                    line += "output band " + band + "\n"
                else:
                    line += band
        if "fatBS" in self.task:
            output_bands = self.setup_bandpath()
            line += "### band structure section \n"
            for band in output_bands:
                if not band.startswith("#"):
                    line += "output band_mulliken " + band + "\n"
                else:
                    line += band
        if "DOS" in self.task:
            line += "### DOS section \n"
            line += "output atom_proj_dos  -10 0 300 0.05       # Estart Eend n_points broadening\n"
            line += "dos_kgrid_factors 4 4 4                    # auxiliary k-grid\n"
        if "GO" in self.task:
            line += "### geometry optimisation section\n"
            line += "relax_geometry \t bfgs \t 1E-2\n"
            line += "relax_unit_cell \t full \n"
            line += "final_forces_cleaned     .true.\n"
            line += "sc_accuracy_forces 1E-5\n"
        if "phonons" in self.task:
            line += "### phonon band structure \n"
            line += "sc_accuracy_forces 1E-5 # necessary for phonons \n"
            line += "final_forces_cleaned \t .true. \n"
            line += "phonon supercell 2 2 2 \n"
            line += "phonon displacement 0.001 \t\t # displacement in Angström \n"
            line += "phonon symmetry_thresh 1e-6 \n"
            line += "phonon frequency_unit cm^-1 \n"
            line += "phonon hessian phono-perl TDI\n"
            output_bands = self.setup_bandpath()
            for band in output_bands:
                line += "phonon band " + band + "\n"
            line += "### phonon DOS \n"
            line += "phonon free_energy 0 800 801 20\n"
            line += "phonon dos 0 600 600 5 20\n"
            line += "### phonon animations \n"
            for mode in range(len(self.structure.atoms) * 3):
                line += "phonon animation 0 0 0 4 5 20 0 0 0 mode{n}.arc mode{n}.ascii mode{n}.xyz mode{n}.xyz_jmol \n".format(
                    n=mode
                )
        return line

    def adjust_cost(self):
        """ This function adjusts the cluster-specific cost requirements to some defaults."""
        if self.cluster == "taurus":
            if self.cost == "low":
                self.memory = 62
                self.ppn = 24
                self.nodes = 1
                self.walltime = 5
            if self.cost == "medium":
                self.memory = 62
                self.ppn = 24
                self.nodes = 4
                self.walltime = 23
            if self.cost == "high":
                self.memory = 126
                self.ppn = 24
                self.nodes = 4
                self.walltime = 23
        elif self.cluster == "t3000":
            if self.cost == "low":
                self.memory = 60
                self.ppn = 20
                self.nodes = 4
                self.walltime = 150
            if self.cost == "medium":
                self.memory = 128
                self.ppn = 20
                self.nodes = 4
                self.walltime = 150
            if self.cost == "high":
                self.memory = 256
                self.ppn = 20
                self.nodes = 2
                self.walltime = 150

    def adjust_control(self):
        """ This function processes the control.in file to add
        comments that are currently not implemented in the ASE."""
        with open(self.path.joinpath("control.in"), "r+") as file:
            control = file.readlines()
        with open(self.path.joinpath("control.in"), "w") as file:
            for line in control:
                write = False if line.startswith("#") else True
                if write:
                    if "xc" in line:  # corrections to the functional
                        line = self.__adjust_xc(line)
                    elif ("spin" in line) and ("collinear" in line):
                        line += "#default_initial_moment   0      # only necessary if not specified in geometry.in\n"
                    elif "adjust_scf" in line:
                        line = self.__adjust_scf(line)
                        line = self.__adjust_task(line)
                file.write(line)

    def adjust_geometry(self):
        """ This function processes the geometry.in file to add
        symmetry constraints."""
        logging.info("Setting up symmetries for geometry optimisation ...")
        inp = ase.io.read(self.path.joinpath("geometry.in"), format="aims")
        out = ase.io.write(
            self.path.joinpath("geometry.in"), inp, format="aims", scaled=True
        )
        with open(self.path.joinpath("geometry.in"), "a+") as file:
            symblock = self.setup_symmetries()
            try:
                file.write(symblock)
            except:
                logging.error(
                    "No symmetries written to geometry.in. Maybe the system is not symmetric enough?"
                )

    def write_submit_t3000(self):
        """ Writes the .sh file to submit on the t3000 via qsub. """
        for i in self.task:
            self.name += "_{}".format(i)
        self.adjust_cost()
        with open(self.path.joinpath("submit.sh"), "w+") as file:
            file.write(
                """#! /bin/sh
#PBS -N {name}
#PBS -l walltime={walltime}:00:00,mem={memory}GB,nodes={nodes}:ppn={ppn}
module ()
    eval `/usr/bin/modulecmd bash $*`
    module load aims
export OMP_NUM_THREADS=1

cd $PBS_O_WORKDIR

mpirun -np {cpus} bash -c "ulimit -s unlimited && aims.171221_1.scalapack.mpi.x" < /dev/null > aims.out
                """.format(
                    name=self.name,
                    cpus=self.nodes * self.ppn,
                    walltime=self.walltime,
                    memory=self.memory,
                    nodes=self.nodes,
                    ppn=self.ppn,
                )
            )

    def write_submit_taurus(self):
        """ Writes the .sh file to submit on the taurus via sbatch. """
        for i in self.task:
            self.name += "_{}".format(i)
        self.adjust_cost()
        with open(self.path.joinpath("submit.sh"), "w+") as file:
            file.write(
                """#!/bin/bash
#SBATCH --time={walltime}:00:00     \t\t\t# walltime in h
#SBATCH --nodes={nodes}             \t\t# number of nodes
#SBATCH --ntasks-per-node={ppn}     \t# cpus per node
#SBATCH --exclusive                 # assert that job takes full nodes
#SBATCH --mem-per-cpu={memory}MB    \t# memory per node per cpu (1972MB on romeo)
#SBATCH -J {name}                   # job name  
#SBATCH --error=slurm.err           \t# stdout
#SBATCH --output=slurm.out          \t# stderr
##SBATCH --partition=haswell64      \t# partition name, can also be gpu2 or romeo
##SBATCH --gres=gpu:4               \t# using 4 gpus per node

# when using gpus, assert that use_gpu is in control.in !
# gpu1 partition will not be supported by the end of the year

module use /home/kempt/Roman_AIMS_env/modules
module load aims_env

echo "slurm job ID: $SLURM_JOB_ID"

# srun_aims is a bash script given by aims_env that executes the AIMS binary and sets additional environment variables
source srun_aims > aims.out
            """.format(
                    name=self.name,
                    ppn=self.ppn,
                    memory=int(int(self.memory) * 1000 / (self.ppn)),
                    walltime=self.walltime,
                    nodes=self.nodes,
                )
            )
