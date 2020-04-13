import os
import numpy as np
from vasplib.core.structure import Structure

class Xdatcar(object):
    """
    Class for reading and analyzing XDATCAR file.
    """
    def __init__(self, filename = 'XDATCAR'):
        """
        Initiate an Xdatcar object with the filename.
        Args:
            filename (str): the name of the file, default to XDATCAR
        """
        self.filename = filename
        self._comment, self._exist_symbols, self._atoms, self._lattice_changed = self._initialize()

    def _initialize(self):
        """
        Returns: (_comment, _exist_symbols, _atoms, _lattice_changed)
                _atoms (list of dict): Each type of atom is represented by a dictionary:
                    {'element': (str), 'num': (int)}
                _lattice_changed (bool): true if the lattice vectors changed
        """
        fp = open(self.filename, 'r')
        # read the comment
        line = fp.readline()
        _comment = line.strip()
        # go to the 6th line
        for i in range(1, 6):
            line = fp.readline()
            line = line.lstrip()
            _exist_symbols = not line[0].isdigit()

        _atoms = []
        if _exist_symbols:
            next_line = fp.readline()
            for symbol, num in zip(line.split(), next_line.split()):
                _atoms.append({'element': symbol, 'num': int(num)})
        else:
            for num in line.split():
                _atoms.append({'element': None, 'num': int(num)})

        for atom in _atoms:
            for i in range(atom['num']):
                fp.readline()
        for i in range(3):
            line_next_block = fp.readline()
        _lattice_changed = line_next_block.strip() == _comment

        fp.close()

        return _comment, _exist_symbols, _atoms, _lattice_changed
        
    def structure(self, n):
        """
        Read a structure from XDATCAR file, configuration no. = n
        Args:
            filename (str): the filename of XDATCAR file.
            n (int): the configuration number, n >= 1.
        """
        res = Structure(comment = self._comment, atoms = self._atoms)
        N = sum([atom['num'] for atom in self._atoms])
        if self._lattice_changed:
            if self._exist_symbols:
                line_lattice = (N + 8) * (n - 1) + 2
                line_coord_type = (N + 8) * (n - 1) + 7
            else:
                line_lattice = (N + 7) * (n - 1) + 2
                line_coord_type = (N + 7) * (n - 1) + 6
        else:
            line_lattice = 2
            if self._exist_symbols:
                line_coord_type = 7 + (N + 1) * (n - 1)
            else:
                line_coord_type = 6 + (N + 1) * (n - 1)
        line_factor = line_lattice - 1

        with open(self.filename, 'r') as fp:
            for i in range(line_factor):
                fp.readline()
            factor = float(fp.readline().strip())
            a = [float(num) for num in fp.readline().strip().split()]
            b = [float(num) for num in fp.readline().strip().split()]
            c = [float(num) for num in fp.readline().strip().split()]
            res.lattice = np.array([a, b, c]) * factor

            for i in range(line_coord_type - line_lattice - 3):
                fp.readline()
            str_coord_type = fp.readline().strip()
            res.coord_type = 'direct' if str_coord_type[0] in 'dD' else 'cart'

            for atom in res.atoms:
                atom['coords'] = []
                for i in range(atom['num']):
                    line = fp.readline().strip()
                    atom['coords'].append([float(num) for num in line.split()[:3]])
            if res.coord_type == 'cart':
                for atom in res.atoms:
                    atom['coords'] = np.array(atom['coords']) * factor
            else:
                for atom in res.atoms:
                    atom['coords'] = np.array(atom['coords'])

        return res
