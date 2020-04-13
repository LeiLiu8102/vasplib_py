import os
import numpy as np
from vasplib.core.structure import Structure

class Chgcar(object):
    """
    Class for reading CHGCAR files.
    """
    def __init__(self, filename = "CHGCAR"):
        """
        Create a CHGCAR file object.
        Args:
            filename (str): the filename of the file to read, default to 'CHGCAR'
        """
        self.filename = filename
        self.NX, self.NY, self.NZ = self.getNxyz() # store the number of grid points
        self.struct = Structure()
        self.struct.from_POSCAR(filename) # store the structure

    def getNxyz(self):
        """
        Get the grid dimensions along x, y and z directions.
        Returns:
            [NX, NY, NZ]: list(int)
        """
        with open(self.filename, 'r') as fp:
            line = fp.readline()
            while line.strip() != '':
                line = fp.readline()
            line = fp.readline()

        NX, NY, NZ = [int(x) for x in line.split()]

        return [NX, NY, NZ]

    def getChargeDensity(self):
        """
        Get the charge density in real space.
        Returns:
            density (NZ * NY * NX np.ndarray):
                unit: electron / grid
        """
        NX, NY, NZ = self.NX, self.NY, self.NZ
        with open(self.filename, 'r') as fp:
            line = fp.readline()
            while line.strip() != '':
                line = fp.readline()
            line = fp.readline()

            density = []
            line = fp.readline()
            while line and 'a' not in line:
                density.extend([float(x) for x in line.split()])
                line = fp.readline()

        density = np.reshape(density, (NZ, NY, NX)) / (NX * NY * NZ)
        return density

    def mean2D(self, plane, label = 'distance'):
        """
        Return the average density along a certain plane. 
        Args:
            plane (str): 'xy' or 'xz' or 'yz'
            label (str): "grid" or "distance"
        Returns:
            X (n2 * 1 np.array), Y (n1 * 1 np.array), Z (n1 * n2 np.array)
                unit: electron / grid
        """
        # No. of grids
        NX, NY, NZ = self.NX, self.NY, self.NZ
        # Get the density along the axis on each grid point
        density = self.getChargeDensity()

        if plane == 'xy':
            Z = np.mean(density, axis = 0)
        elif plane == 'xz':
            Z = np.mean(density, axis = 1)
        elif plane == 'yz':
            Z = np.mean(density, axis = 2)

        num_row, num_col = Z.shape
        if label == 'grid':
            X = np.arange(num_row)
            Y = np.arange(num_col)
        elif label == 'distance':
            a, b, c = self.struct.lattice_constants[:3]
            if plane == 'xz':
                X = np.arange(num_col)/NX*a
                Y = np.arange(num_row)/NZ*c
            elif plane == 'xy':
                X = np.arange(num_col)/NX*a
                Y = np.arange(num_row)/NY*b
            elif plane == 'yz':
                X = np.arange(num_col)/NY*b
                Y = np.arange(num_row)/NZ*c

        return X, Y, Z

    def mean1D(self, axis, label):
        """
        Return the average density along a certain x. The cross-section plane to
        sum is normal to the direction "axis".
        Args:
            axis (str): 'x' or 'y' or 'z', indicating the axis
            label (str): "grid" or "distance" or "atom"
                When label == 'atom', we only support charge density along
                x axis.
        Returns:
            result (n * 2 np.array)
        """

        # No. of grids
        NX, NY, NZ = self.NX, self.NY, self.NZ

        # Get the density along the axis on each grid point
        density = self.getChargeDensity()

        if axis == 'x':
            density_1D = np.mean(density, (0, 1))
        elif axis == 'y':
            density_1D = np.mean(density, (0, 2))
        elif axis == 'z':
            density_1D = np.mean(density, (1, 2))

        if label == 'grid':
            independent = np.arange(density_1D.size)
        elif label == 'distance':
            a, b, c = self.struct.lattice_constants[:3]
            if axis == 'x':
                independent = np.arange(density_1D.size)/NX*a
            elif axis == 'y':
                independent = np.arange(density_1D.size)/NY*b
            elif axis == 'z':
                independent = np.arange(density_1D.size)/NZ*c
        elif label == 'atom':
            if axis == 'x':
                # direct x coordinates of all the atoms
                atom_x = self.struct.direct_coords()[:, 0]
                # fractional x length between neighboring grid points
                length_per_section = 1.0/NX
                # length for atom 0 to its left side
                heading = (atom_x[0] + 1 - atom_x[-1])/2

                bisect_x = []
                for i in range(len(atom_x) - 1):
                    bisect_x.append((atom_x[i] + atom_x[i + 1])/2)

                density_accu = [] # store the density of all the atoms, except the
                                  # atom 0 and the last atom

                for i in range(len(atom_x) - 2):
                    left = np.round(bisect_x[i]/length_per_section)
                    right = np.round(bisect_x[i + 1]/length_per_section)
                    density_accu.append(np.sum(density_1D[int(left): int(right)]))
                
                # calculate the density for atom 0
                if heading > atom_x[0]:
                    # contribute at the tail to be counted for atom 0
                    left = 0
                    right = np.round(bisect_x[0]/length_per_section)
                    density_atom_0 = np.sum(density_1D[int(left) : int(right)])

                    left = np.round((1-heading+atom_x[0])/length_per_section)
                    right = NX + 1
                    density_atom_0 += np.sum(density_1D[int(left) : int(right)])

                    left = np.round(bisect_x[-1]/length_per_section)
                    right = np.round((1-heading+atom_x[0])/length_per_section)
                    density_atom_last = np.sum(density_1D[int(left) : int(right)])

                elif heading <= atom_x[0]:
                    # no contribute at the tail region for atom 0
                    left = np.round((atom_x[0] - heading)/length_per_section)
                    right = np.round(bisect_x[0]/length_per_section)
                    density_atom_0 = np.sum(density_1D[int(left) : int(right)])

                    # the last atom
                    left = 0
                    right = np.round((atom_x[0] - heading)/length_per_section)
                    density_atom_last = np.sum(density_1D[int(left) : int(right)])
                    left = np.round(bisect_x[-1]/length_per_section)
                    right = NX + 1
                    density_atom_last += np.sum(density_1D[int(left) : int(right)])

                density_1D = [density_atom_0] + density_accu + [density_atom_last]
                independent = np.arange(len(atom_x))

        result = np.concatenate(([independent], [density_1D]), axis = 0)
        result = np.transpose(result)

        return result
