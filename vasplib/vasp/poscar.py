# coding: utf-8

import math
from vasplib.analysis.build import Build
import numpy as np
import itertools

"""
Class for reading, manipulating, and writing POSCAR and structure.
"""

class Poscar(Build):
    """
    Poscar object for reading, writing structure and POSCAR files.
    Selective dynamics not allowed.
    """
    def __init__(self,
                comment = 'Default comment',
                factor = 1.0,
                lattice = np.empty((0,3)),
                lattice_flag = [],
                atoms = [],
                coord_type = 'cart',
                selective = False,
                ):
        """
        Create a Poscar object.
        Args:
            comment (str): the comment for the POSCAR.
            factor (float): the scaling factor used to scale all lattice vectors and all atomic coordinates.
                if factor < 0: it is interpreted as the total volume of the cell.
            lattice (3*3 np.array, float): the three reduced lattice vectors defining the unit cell.
                e.g., np.array([[11, 0, 0],
                       [0, 12, 0],
                       [0, 0, 13]])
            lattice_flag ( 3*3 bool list): the flags for each component of the lattice signaling whether the
                respective coordinates will be allowed to change during the ionic relaxation.
                e.g., [[True, True, False],
                       [True, True, False],
                       [False, False, False]]
            coord_type (str): 'cart' or 'direct', representing the coordination type of the structure.
            atoms (list): the list representing the atomic elements, numbers and coordinations.
                Each type of atom is represented by a dictionary:
                    {'element': (str),
                    'num': (int),
                    'coords': (num*3 np.array, float),
                    'selective': (num * 3 bool list)}
            selective (bool): whether "Selective Dynamics" are switched on
        """
        Build.__init__(self, comment, lattice, atoms, coord_type)
        self.factor = factor
        self.lattice_flag = lattice_flag
        self.selective = selective
        self.normalize_factor()

    def normalize_factor(self):
        """
        Unify the factor to 1.0
        """
        if not math.isclose(self.factor, 1.0, rel_tol=1e-6):
            self.lattice *= factor
            if self.coord_type == 'cart':
                for atom in self.atoms:
                    atom['coord'] *= factor
            self.factor = 1

    def from_POSCAR(self, filename = 'POSCAR'):
        """
        Read POSCAR file.
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
        self.facotr = 1

        reduced_lattice = []
        self.lattice_flag = []
        # 3rd ~ 5th line: lattice vectors
        for i in range(2, 5):
            line = lines[i].split()
            vector = [float(num) for num in line[:3]]
            reduced_lattice.append(vector)
            if len(line) > 3:
                self.lattice_flag.append(line[3:6])
                for item in line[3:6]:
                    if item not in 'TF':
                        raise ValueError("Illegal lattice flags in {}!".format(lines[i]))
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
        self.selective = False
        if lines[num_line][0] in 'sS':
            self.selective = True
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
            if self.selective:
                atom['selective'] = []
            for i in range(atom['num']):
                line = lines[num_line]
                atom['coords'].append([float(num) for num in line.split()[:3]])
                if self.selective:
                    atom['selective'].append(line.split()[3:6])
                num_line += 1

        if self.coord_type == 'cart':
            for atom in self.atoms:
                atom['coords'] = np.array(atom['coords']) * factor
        else:
            for atom in self.atoms:
                atom['coords'] = np.array(atom['coords'])

    def write_POSCAR(self, filename):
        """
        Write Poscar object to a file.
        Args:
        filename (str): the filename to write to.
        """
        # Convert bool to char
        def bool_char(val):
            """Return 'T' if  True, return 'F' if False."""
            return 'T' if val else 'F'

        with open(filename, 'w') as fp:
            fp.write(self.comment + '\n')
            fp.write('{:.14f}\n'.format(self.factor))

            # Write the lattice vectors and their flags
            if self.lattice_flag:
                for i in range(3):
                    bool_vector_str = [bool_char(flag) for flag in self.lattice_flag[i]]
                    fp.write('{:.14f}    {:.14f}    {:.14f}'.format(*self.lattice[i]))
                    fp.write('    ' + '  '.join(bool_vector_str))
                    fp.write('\n')
            else:
                for i in range(3):
                    fp.write('{:.14f}    {:.14f}    {:.14f}'.format(*self.lattice[i]))
                    fp.write('\n')

            # Write the atomic species
            fp.write(' '.join([atom['element'] for atom in self.atoms]))
            fp.write('\n')
            # Write the atom numbers
            fp.write(' '.join([str(atom['num']) for atom in self.atoms]))
            fp.write('\n')
            # Write selective dynamics
            if self.selective:
                fp.write("Selective Dynamics\n")
            # Write the coordination type
            fp.write(self.coord_type + '\n')
            # Write the atomic positions
            for atom in self.atoms:
                for i in range(atom['num']):
                    fp.write('{:.14f}    {:.14f}    {:.14f}'.format(*atom['coords'][i]))
                    if self.selective:
                        fp.write('    ' + ' '.join([bool_char(x) for x in atom['selective'][i]]))
                    fp.write('\n')
###########################################################################################
    def update_elements(self, elements):
        """
        Update the elements in the Poscar object with the elements provided.
        Args:
        elements (list): containing the symbols (str) of the elements.
        """
        for i in range(len(elements)):
            self.atoms[i]['element'] = elements[i]

    def swap_idx(self, idx1, idx2):
        """
        Swap the positions of atoms idx1 and idx2.
        Args:
        idx1, idx2 (int): the index of the atoms to exchange.
            0 <= idx1, idx2 < self.get_total_nums()
        """
        nums = [atom['num'] for atom in self.atoms]
        ele1 = 0
        ele2 = 0
        for num in nums:
            if idx1 - num <= -1:
                break
            else:
                idx1 -= num
                ele1 += 1
        for num in nums:
            if idx2 - num < 0:
                break
            else:
                idx2 -= num
                ele2 += 1
        self.atoms[ele1]['reduced_coords'][idx1], self.atoms[ele2]['reduced_coords'][idx2]\
                = self.atoms[ele2]['reduced_coords'][idx2], self.atoms[ele1]['reduced_coords'][idx1]

    def swap_positions(self, atom1, atom2):
        """
        Swap the positions of atom1 and atom2.
        Args:
        atoms1, atom2 (tuple): (ele_idx, atom_idx)
            0 <= idx
        """
        self.atoms[atom1[0]]['redcued_coords'][atom1[1]], self.atoms[atom2[0]]['reduced_coords'][atom2[1]]\
              = self.atoms[atom2[0]]['reduced_coords'][atom2[1]], self.atoms[atom1[0]]['reduced_coords'][atom1[1]]
