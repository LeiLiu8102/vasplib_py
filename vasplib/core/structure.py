# conding: utf-8
import numpy as np
import math
from copy import deepcopy
from vasplib.core.periodic_table import Element
from scipy.constants import N_A

class Structure(object):
    """
    Structure object for reading, writing and manipulating structures.
    """
    def __init__(self,
            comment = 'Default comment',
            lattice = [],
            atoms = [],
            coord_type = None
            ):
        """
        Create a periodic structure.
        Args:
            comment (str): string representing the structure.
            lattice (3*3 np.array, float): the three reduced lattice vectors defining the unit cell.
                e.g., np.array([[11, 0, 0],
                       [0, 12, 0],
                       [0, 0, 13]])
            atoms (list): the list representing the atomic elements, numbers and coordinations.
                Each type of atom is represented by a dictionary:
                    {'element': (str),
                    'num': (int),
                    'coords': (num*3 np.array, float)}
            coord_type (str): 'cart' or 'direct', representing the coordination type of the structure.
        """
        self.comment = comment
        self.lattice = lattice
        self.atoms = atoms
        self.coord_type = coord_type

    @property
    def molar_mass(self):
        """
        Return the molar mass of the structure in one unit cell.
        Returns:
            molar mass (float): unit: g/mol
        """
        return sum(Element(atom['element']).get_attr('Atomic mass')* atom['num'] for atom in self.atoms)

    @property
    def density(self):
        """
        Return the density of the structure.
        Returns:
            density (float): unit: g/cm^3
        """
        mass = self.molar_mass/N_A
        volume = np.linalg.det(self.lattice)*10**(-24)
        return mass/volume

    def mass_center(self):
        """
        Return the mass center of the structure.
        Returns:
            center (np.array): np.array([x, y, z])
        """
        weight = self.molar_mass
        weighted_sum = 0
        for species in self.atoms:
            weighted_sum += np.sum(species['coords'], axis = 0) * Element(species['element']).get_attr('Atomic mass')
        center = weighted_sum / weight

        return center

    def from_POSCAR(self, filename = 'POSCAR'):
        """
        Read a structure from POSCAR file.
        Args:
            filename (str): the filename of the POSCAR file. Defalut to 'POSCAR'
        """
        with open(filename, 'r') as fp:
            lines = fp.readlines()

        # Remove comments starting with '!' or "#",
        # and remove leading/tailing spaces, EOL
        def beautify(string):
            string = string.strip()
            if '!' in string:
                string = string.split('!', 1)[0]
            if '#' in string:
                string = string.split('#', 1)[0]
            string = string.strip()
            return string

        # Remove the empty lines and lines with only comments
        for i, line in enumerate(lines):
            lines[i] = beautify(line)
            if not lines[i]:
                lines.remove(lines[i])

        # 1st line: comment
        self.comment = lines[0]
        # 2nd line: factor
        factor = float(lines[1])

        reduced_lattice = []
        # 3rd ~ 5th line: lattice vectors
        for i in range(2, 5):
            line = lines[i].split()
            vector = [float(num) for num in line[:3]]
            reduced_lattice.append(vector)
        self.lattice = np.array(reduced_lattice) * factor

        self.atoms = []
        # 6th line: atomic species and numbers
        if lines[5][0].isdigit(): # No line for atomic species
            for num_str in lines[5].split():
                self.atoms.append({'element': None, 'num': int(num_str)})
            num_line = 6 # line for coord_type
        else:
            for element, num_str in zip(lines[5].split(), lines[6].split()):
                self.atoms.append({'element': element, 'num': int(num_str)})
            num_line = 7

        # Skip "Selective Dynamics"
        if lines[num_line][0] in 'sS':
            num_line += 1
            
        # Atomic coordination type
        if lines[num_line][0] in "dD":
            self.coord_type = 'direct'
        elif lines[num_line][0] in "cC":
            self.coord_type = 'cart'
        else:
            raise Exception ("Undefined coordination type in {}".format(filename))

        num_line += 1
        # Atomic positions
        for atom in self.atoms:
            atom['coords'] = []
            for i in range(atom['num']):
                line = lines[num_line]
                atom['coords'].append([float(num) for num in line.split()[:3]])
                num_line += 1

        if self.coord_type == 'cart':
            for atom in self.atoms:
                atom['coords'] = np.array(atom['coords']) * factor
        else:
            for atom in self.atoms:
                atom['coords'] = np.array(atom['coords'])

    def write_POSCAR(self, filename):
        """
        Write Structure object to a file.
        Args:
        filename (str): the filename to write to.
        """
        # Convert bool to char
        def bool_char(val):
            """Return 'T' if  True, return 'F' if False."""
            return 'T' if val else 'F'

        with open(filename, 'w') as fp:
            fp.write(self.comment + '\n')
            fp.write('1.0\n')

            # Write the lattice vectors
            for i in range(3):
                fp.write('     '.join([str(num) for num in self.lattice[i]]))
                fp.write('\n')

            # Write the atomic species
            fp.write(' '.join([atom['element'] for atom in self.atoms]))
            fp.write('\n')
            # Write the atom numbers
            fp.write(' '.join([str(atom['num']) for atom in self.atoms]))
            fp.write('\n')
            # Write the coordination type
            fp.write(self.coord_type + '\n')
            # Write the atomic positions
            for atom in self.atoms:
                for i in range(atom['num']):
                    fp.write('    '.join([str(num) for num in atom['coords'][i]]))
                    fp.write('\n')

    def direct_to_cart(self):
        """
        Change the style of the coordinations to cartesian.
        """
        if self.coord_type == 'direct':
            self.coord_type = 'cart'
            for atom in self.atoms:
                atom['coords'] = np.matmul(atom['coords'], self.lattice)

    def cart_to_direct(self):
        """
        Change the style of the coordinations to direct.
        """
        if self.coord_type == 'cart':
            self.coord_type = 'direct'
            for atom in self.atoms:
                atom['coords'] = np.matmul(atom['coords'], np.linalg.inv(self.lattice))

    @property
    def elements(self):
        """
        Return the elements list of the structure.
        Returns:
            elements (list): [ele0, ele1, ...], each element represented by a string.
        """
        return [atom['element'] for atom in self.atoms]

    @property
    def atom_nums(self):
        """
        Return the total number of atoms in the structure.
        Returns:
            (int)
        """
        return sum([atom['num'] for atom in self.atoms])

    @property
    def atoms_flat(self):
        """
        Return a flat list representation of all the atoms and their coords
        e.g., [{'element': 'Al', 'coord': np.array([0, 0, 0])}]
        """
        atoms_coords = []
        for element in self.atoms:
            for coord in element['coords']:
                temp = {'element': element['element'], 'coord': coord}
                atoms_coords.append(temp)
        return atoms_coords

    @property
    def reciprocal_lattice(self):
        """
        Return the reciprocal lattice vector of the Poscar object.
        Returns:
            3 * 3 np.array: [b1, b2, b3]
        """
        return np.transpose(np.linalg.inv(self.lattice))

    @property
    def lattice_constants(self):
        """
        Get the lattice parameters of the structure, in the order
        of a, b, c, alpha, belta, gamma.
        Returns:
            [a, b, c, d, alpha, beta, gamma], angle unit: degree
        """
        [a, b, c] = np.linalg.norm(self.lattice, axis = 1)
        def angle(v1, v2):
            division = np.dot(v1, v2)/(np.linalg.norm(v1) * np.linalg.norm(v2))
            return np.degrees(np.arccos(division))
        alpha = angle(self.lattice[1], self.lattice[2])
        beta = angle(self.lattice[2], self.lattice[0])
        gamma = angle(self.lattice[0], self.lattice[1])
        return [a, b, c, alpha, beta, gamma]

    def cartesian_coords(self):
        """
        List the cartesian coordinations of all the atoms.
        Returns:
            self.atom_nums * 3 np.array
        """
        coords = np.concatenate([atom['coords'] for atom in self.atoms], axis = 0)
        if self.coord_type == 'direct':
            return np.matmul(coords, self.lattice)
        return coords

    def direct_coords(self):
        """
        List the fractional coordinations of all the atoms.
        Returns:
            self.atom_nums * 3 np.array
        """
        coords = np.concatenate([atom['coords'] for atom in self.atoms], axis = 0)
        if self.coord_type == 'cart':
            return np.matmul(coords, np.linalg.inv(self.lattice))
        return coords