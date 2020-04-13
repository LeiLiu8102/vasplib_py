# coding: utf-8
import numpy as np
from vasplib.core.structure import Structure
import copy

class Build(Structure):
    """
    Class for manipulate structures.
    """
    def __init__(self,
            comment = 'Default comment',
            lattice = [],
            atoms = [],
            coord_type = None
            ):
        Structure.__init__(self, comment, lattice, atoms, coord_type)

    def supercell(self, P, inplace = True):
        """
        Make supercell
        Args:
            P (list(int)): duplicates along a, b and c axis, P[i] is positive integers.
            inplace (bool): whether modify the structure in place, default to True
        """
        if inplace:
            if self.coord_type == 'cart':
                for atom in self.atoms:
                    original_coords = atom['coords']
                    atom['coords'] = np.empty((0, 3))
                    for i in range(int(P[0])):
                        for j in range(int(P[1])):
                            for k in range(int(P[2])):
                                atom['coords'] = np.concatenate((atom['coords'], original_coords + np.matmul([[i, j, k]], self.lattice)))
                    atom['num'] = len(atom['coords'])
                self.lattice = self.lattice * [[P[0]], [P[1]], [P[2]]]

            if self.coord_type == 'direct':
                for atom in self.atoms:
                    original_coords = atom['coords']
                    atom['coords'] = np.empty((0, 3))
                    for i in range(int(P[0])):
                        for j in range(int(P[1])):
                            for k in range(int(P[2])):
                                atom['coords'] = np.concatenate((atom['coords'], original_coords/P + [i/P[0], j/P[1], k/P[2]]))
                    atom['num'] = len(atom['coords'])
                self.lattice = self.lattice * [[P[0]], [P[1]], [P[2]]]

        else:
            s = copy.deepcopy(self)
            if s.coord_type == 'cart':
                for atom in s.atoms:
                    original_coords = atom['coords']
                    atom['coords'] = np.empty((0, 3))
                    for i in range(int(P[0])):
                        for j in range(int(P[1])):
                            for k in range(int(P[2])):
                                atom['coords'] = np.concatenate((atom['coords'], original_coords + np.matmul([[i, j, k]], s.lattice)))
                    atom['num'] = len(atom['coords'])
                s.lattice = s.lattice * [[P[0]], [P[1]], [P[2]]]

            if s.coord_type == 'direct':
                for atom in s.atoms:
                    original_coords = atom['coords']
                    atom['coords'] = np.empty((0, 3))
                    for i in range(int(P[0])):
                        for j in range(int(P[1])):
                            for k in range(int(P[2])):
                                atom['coords'] = np.concatenate((atom['coords'], original_coords/P + [i/P[0], j/P[1], k/P[2]]))
                    atom['num'] = len(atom['coords'])
                s.lattice = s.lattice * [[P[0]], [P[1]], [P[2]]]
                
            return s

    def permute_atom(self, idx, displacement, inplace = True):
        """
        Permute the atom i by the displacement.
        Args:
            idx (int): the atom index
            displacement (list(float)): displacement vector along x, y, and z axis
            inplace (bool): whether modify the structure in place, default to True
        """
        # Change the structure in place
        if inplace:
            for element in self.atoms:
                if idx >= element['num']:
                    idx -= element['num']
                elif idx >= 0:
                    element['coords'][idx] = element['coords'][idx] + displacement
                    idx = -1
                else:
                    break

            if idx > 0:
                raise ValueError("The atom idx {} exceeds the number of atoms.".format(idx))

        # Return a permuted structure
        else:
            s = copy.deepcopy(self)

            for element in s.atoms:
                if idx >= element['num']:
                    idx -= element['num']
                else:
                    element['coords'][idx] = element['coords'][idx] + displacement
                    idx = 0
            if idx > 0:
                raise ValueError("The atom idx {} exceeds the number of atoms.".format(idx))
            return s