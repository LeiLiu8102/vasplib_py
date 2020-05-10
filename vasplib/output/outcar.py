import os
import numpy as np
from vasplib.core import periodic_table as pt
from vasplib.core.structure import Structure
import subprocess as sp

class Outcar(object):
    """
    Class for reading OUTCAR files.
    Attributes:
        filename (str)
        cutoff (float)
    Property:
        ispin
        efermi
        nkpts
        nbands
    Methods:
        exists()
        get_species()
        initial_struct()

    """
    def __init__(self, filename = "OUTCAR", cutoff = 0.01):
        """
        Create a Outcar file object.
        Args:
            filename (str): the filename of the file to read.
            cutoff (float): the minimum occupancy to be considered occupied band, default to 0.01
        """
        self.filename = filename
        self.cutoff = cutoff

    def exists(self):
        """
        Decide whether the OUTCAR file exists.
        Returns:
            (bool): True or False
        """
        return os.path.isfile(self.filename)

    @property
    def ispin(self):
        """
        Get the ISPIN vale from the file.
        Returns:
            ISPIN (int): 1 or 2
        """
        with open(self.filename, 'r') as fp:
            for line in fp:
                if 'ISPIN' in line:
                    return int(line.split()[2])

    @property
    def efermi(self):
        """
        Get the fermi energy of the Outcar object.
        Returns:
            E-fermi (float): fermi energy in eV.
        """
        with open(self.filename, 'r') as fp:
            for line in fp:
                if 'E-fermi' in line:
                    return float(line.split()[2])

    @property
    def nkpts(self):
        """
        Get the number of kpoints in BZ.
        Returns:
            nkpts (int)
        """
        with open(self.filename, 'r') as fp:
            for line in fp:
                if 'NKPTS' in line:
                    return int(line.split()[3])

    @property
    def nbands(self):
        """
        Get the number of electronic bands.
        Returns:
            nbands (int)
        """
        with open(self.filename, 'r') as fp:
            for line in fp:
                if 'NBANDS' in line:
                    return int(line.split()[14])

    def get_species(self):
        """
        Get the species in the OUTCAR file.
        Returns:
            list[str]
        """
        species = []
        out = sp.run(["grep", "VRHF", self.filename], capture_output=True, text=True).stdout
        for s in out.split('='):
            tmp = s.split(':')
            if len(tmp) > 1:
                species.append(tmp[0].strip())

        # verify the species
        for symbol in species:
            element = pt.Element(symbol)

        return species

    def initial_struct(self):
        """
        Get the initial structure in the OUTCAR file, found by keyword "ion  position".
        Returns:
            Structure
        """
        # the default coordinates are direct
        coord_type = 'direct'
        # Get the species symbols
        species = self.get_species()
        # Get the lattice
        lattice = np.empty((0, 3))
        out = sp.run(["grep", "-A", "4", "  Lattice vectors:", self.filename], capture_output=True, text=True).stdout
        out_list = out.split('\n')
        for i in range(2, 5):
            tmp = out_list[i]
            vector = np.fromstring(tmp.strip(')').split('(')[1], dtype = float, sep=',')
            lattice = np.concatenate((lattice, [vector]), axis = 0)
        # Get the nums of atoms
        nums = []
        nums_bash_out = sp.run(["grep", "ions per type", self.filename], capture_output=True, text=True).stdout
        for x in nums_bash_out.split('=')[1].split():
            nums.append(int(x))
        total_num = sum(nums)
        # Get the locations of atoms by the keyword "ion  position"
        positions = []
        with open(self.filename, 'r') as fp:
            while 'ion  position' not in fp.readline():
                continue
            for next_idx in range(1, total_num + 1):
                line = fp.readline()
                while not line.startswith("   "+str(next_idx)):
                    line = fp.readline()
                position = line.split()[1:4]
                position[-1] = position[-1].rstrip('-')
                position = [float(x) for x in position[:]]
                positions.append(position)
        atoms = []
        num_current = 0
        for element, num in zip(species, nums):
            atom = {'element': element, 'num': num, 
                    'coords': np.array(positions[num_current : num_current + num])}
            num_current += num
            atoms.append(atom)

        struct = Structure(coord_type = coord_type, lattice = lattice, atoms = atoms)

        return struct
        
    def struct_ionic_step(self, i):
        """
        Get the structure in a certain ionic step, found by keyword "POSITION".
        """
        # the default coordinates are direct
        coord_type = 'cart'
        # Get the species symbols
        species = self.get_species()
        # Get the nums of atoms
        nums = []
        nums_bash_out = sp.run(["grep", "ions per type", self.filename], capture_output=True, text=True).stdout
        for x in nums_bash_out.split('=')[1].split():
            nums.append(int(x))
        total_num = sum(nums)
        
        with open(self.filename, 'r') as fp:
            number = str(i)
            while 'Iteration' + number.rjust(7, ' ') not in fp.readline():
                continue
            # find lattice vector
            while "direct lattice vectors" not in fp.readline():
                continue
            lattice = []
            for i in range(3):
                line = fp.readline()
                v = [float(x) for x in line.split()[:3]]
                lattice.append(v)
            # find atomic coordinates
            while 'POSITION' not in fp.readline():
                continue
            fp.readline()
            positions = []
            for i in range(total_num):
                line = fp.readline()
                v = [float(x) for x in line.split()[:3]]
                positions.append(v)

        atoms = []
        num_current = 0
        for element, num in zip(species, nums):
            atom = {'element': element, 'num': num, 
                    'coords': np.array(positions[num_current : num_current + num])}
            num_current += num
            atoms.append(atom)

        struct = Structure(coord_type = coord_type, lattice = np.array(lattice), atoms = atoms)
        return struct

    def energy_ionic_step(self, i):
        """
        Get the energy of the ionic step i, found by keyword "energy(sigma->0)".
        Args:
            i (int): positive integer
        Returns:
            energy (float): total energy, unit: eV
        """
        with open(self.filename, 'r') as fp:
            number = str(i)
            while 'Iteration' + number.rjust(7, ' ') not in fp.readline():
                continue
            line = fp.readline()
            while line:
                if "energy(sigma->0)" in line:
                    energy = float(line.split('=')[-1])
                    line = fp.readline()
                elif 'Iteration{:>7d}'.format(i + 1) in line:
                    break
                else:
                    line = fp.readline()
        return energy

    def dipole_moment_ionic_step(self, i):
        """
        Get the energy of the ionic step i, found by keyword "dipolmoment".
        Args:
            i (int): positive integer
        Returns:
            dipole ([float]): dipole moment of length 3, unit: electrons x Angstrom
        """
        with open(self.filename, 'r') as fp:
            keyword = "Iteration{:>7d}".format(i)
            while keyword not in fp.readline():
                continue
            line = fp.readline()
            while line:
                if "dipolmoment" in line:
                    dipole = [float(x) for x in line.split()[1:4]]
                    line = fp.readline()
                elif 'Iteration{:>7d}'.format(i + 1) in line:
                    break
                else:
                    line = fp.readline()
        return dipole

    def total_force_ionic_step(self, i):
        """
        Get the TOTAL-FORCE from the OUTCAR file from an ionic step.
        Returns:
            atom_nums * 3 np.array, each row representing the force on an atom along x, y, and z direction
        """
        with open(self.filename, 'r') as fp:
            keyword ='Iteration{:>7d}'.format(i)
            while keyword not in fp.readline():
                continue
            while 'TOTAL-FORCE (eV/Angst)' not in fp.readline():
                continue

            tmp = fp.readline()
            line = fp.readline()
            total_force = []
            while not line.endswith('-\n'):
                force = np.fromstring(line, sep = ' ')[3:]
                total_force.append(force)
                line = fp.readline()
            
        return np.array(total_force)

    def end_without_error(self):
        """
        Decide whether the job is finished.
        Returns:
            (bool): True or False
        """
        with open(self.filename, 'r') as fp:
            return "Voluntary context switches" in fp.readlines()[-1]

    def max_iteration(self):
        """
        Return the total numbers of iterations.
        Returns:
            [ionic_steps, electronic_steps] ([int, int])
        """
        with open(self.filename, 'r') as fp:
            for line in fp:
                if "Iteration" in line:
                    key_line = line
        key_line = key_line.strip('-\n')
        left, right = key_line.split('(')
        ionic = int(left.split()[1])
        electronic = int(right.strip(') '))

        return ionic, electronic

    def cbm_vbm(self):
        """
        Get the cbm and vbm value in eV
        Returns:
            list[upcbm, upvbm, dncbm, dnvbm] or [cbm, vbm]
        """
        ISPIN, Fermi, NKPTS, NBANDS = self.ispin, self.efermi, self.nkpts, self.nbands
        index = []
        with open(self.filename, 'r') as fp:
            for i, line in enumerate(fp, 1):
                if 'band No' in line:
                    index.append(i)
            fp.seek(0)
            lines = fp.readlines()
        upocc, upemp, dnocc, dnemp = [], [], [], []
        for i in range(NKPTS):
            for j in range(NBANDS):
                tem = lines[index[i] + j].split()
                if float(tem[2]) >= self.cutoff:
                    upocc.append(float(tem[1]))
                else:
                    upemp.append(float(tem[1]))
        upvbm = max(upocc)
        upcbm = min(upemp)

        if ISPIN ==2:
            for i in range(NKPTS, NKPTS * 2):
                for j in range(NBANDS):
                    tem = lines[index[i] + j].split()
                    if float(tem[2]) >= self.cutoff:
                        dnocc.append(float(tem[1]))
                    else:
                        dnemp.append(float(tem[1]))
            dnvbm = max(dnocc)
            dncbm = min(dnemp)
            return [upcbm, upvbm, dncbm, dnvbm]
        return [upcbm, upvbm]

    def bandgap(self):
        """
        Get the band gap from the OUTCAR file
        returns:
            list ([bandgap_up, bandgap_down] or [bandgap])
        """
        bmm = self.cbm_vbm()
        if len(bmm) == 2:
            return [bmm[0] - bmm[1]]
        else:
            return [bmm[0] - bmm[1], bmm[2] - bmm[3]]

    def macro_dielectric_tensor(self):
        """
        Get the the field "macrospcopic static dielectric tensor (including local field effects in DFT)".
        Returns:
            tensor (3 * 3 np.array): the dielectric tensor
        """
        # Find the last occurrence of dielectric tensor
        last_occurrence = 0
        with open(self.filename, 'r') as fp:
            for n, line in enumerate(fp):
                if line.endswith("MACROSCOPIC STATIC DIELECTRIC TENSOR (including local field effects in DFT)\n"):
                    last_occurrence = n
        tensor = []
        with open(self.filename, 'r') as fp:
            for n, line in enumerate(fp):
                if n in range(last_occurrence + 2, last_occurrence + 5):
                    tensor.append(np.fromstring(line, dtype = float, sep = ' '))
        return np.array(tensor)

    def imaginary_dielectric_function(self):
        """
        Get the frequency-dependent imaginary dielectric function.
        Returns:
            epsilon: np.ndarrary with seven columns, the first column is energy (eV), 
                    the second to the seventh represent the xx, yy, zz, xy, yz, and zx components.
        """
        epsilon = []
        with open(self.filename, 'r') as fp:
            while not fp.readline().startswith("  frequency dependent IMAGINARY DIELECTRIC FUNCTION"):
                continue
            _ = fp.readline()
            _ = fp.readline()

            line = fp.readline()
            while line.strip():
                row = np.fromstring(line, dtype = float, sep = ' ')
                epsilon.append(row)
                line = fp.readline()


        epsilon = np.array(epsilon)
        return epsilon



