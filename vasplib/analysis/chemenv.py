# coding: utf-8
import numpy as np
from vasplib.core.structure import Structure

class LocalEnv(Structure):
    """
    Class for analyzing the local environment of a structure.
    """
    def __init__(self,
            comment = 'Default comment',
            lattice = [],
            atoms = [],
            coord_type = None
            ):
        Structure.__init__(self, comment, lattice, atoms, coord_type)
        self._normalize()

    def _normalize(self):
        """
        Find the image atoms in the structure within the fractional range of [0, 1]
        along a, b, and c directions, by applying translatioal symmetry.
        The method doesn't change the coord_type of the object.
        e.g., [-0.1, 0.3, 0.5] --> [0.9, 0.3, 0.5]
        """
        original_coord_type = self.coord_type
        self.cart_to_direct()
        for atom in self.atoms:
            atom['coords'] = atom['coords'] % 1

        if original_coord_type == 'cart':
            self.direct_to_cart()

    def periodic_sites(self, i, axrange):
        """
        Get the periodic sites of atom i within the axis range, including the atom itself
        Args:
            i (int): the index of the atom. 0 <= i < atom['nums']
            axrange (list): [xmin, xmax, ymin, ymax, zmin, zmax]
        Returns:
            n * 3 np.array: the direct coordinations of all the periodic sites.
        """
        coord = self.direct_coords()[i]
        coords = []
        for ix in range(int(axrange[0] - coord[0])//1, int(axrange[1] - coord[0])//1 + 1):
            for iy in range(int(axrange[2] - coord[1])//1, int(axrange[3] - coord[1])//1 + 1):
                for iz in range(int(axrange[4] - coord[2])//1, int(axrange[5] - coord[2])//1 + 1):
                    coords.append(coord + np.array([ix, iy, iz]))
        return np.array(coords)

    def neighbors(self, i, cutoff = 8):
        """
        Get all the neighbors of atom i within the cutoff distance, including the atom itself
        Args:
            i (int): 0 <= i < self.atom_nums
        Returns:
            neighbors (list of tuples (atom_idx, direct_coord, distance))
        """
        coord = self.direct_coords()[i]
        Nmax = cutoff * np.linalg.norm(self.reciprocal_lattice, axis = 1)
        upper = Nmax + coord
        lower = -Nmax + coord
        axrange = [lower[0], upper[0], lower[1], upper[1], lower[2], upper[2]]
        neighbors = []
        for i in range(self.atom_nums):
            neis = self.periodic_sites(i, axrange)
            for nei in neis[:]:
                distance = np.linalg.norm(np.matmul(nei - coord, self.lattice))
                if distance < cutoff:
                    neighbors.append((i, nei, distance))
        return neighbors

    def neighbors_shell(self, i, shell = 1, cutoff = 8, tol = 0.1):
        """
        Args:
            i (int): 0 <= i < self.atom_nums
            shell (int): index of the shell, starting from 1
            cutoff (float): cutoff radius for searching neighbors, default to 8.0
            tol (float): tolerance parameter for determining a neighbor, default to 0.1 (Ang)
        """
        neighbors = sorted(self.neighbors(i, cutoff), key = lambda item: item[2])
        cur_atom = 0
        for i in range(shell - 1):
            cur_atom += 1
            cur_dist = neighbors[cur_atom][2]
            while neighbors[cur_atom + 1][2] < cur_dist + tol:
                cur_atom += 1

        ans = []
        cur_atom += 1
        cur_dist = neighbors[cur_atom][2]
        while neighbors[cur_atom][2] < cur_dist + tol:
            ans.append(neighbors[cur_atom])
            cur_atom += 1

        return ans  