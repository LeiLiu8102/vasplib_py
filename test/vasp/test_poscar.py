import os
import unittest
import vasplib
from vasplib.vasp.poscar import Poscar
import copy

class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        p = Poscar()
        p.from_POSCAR(os.path.join(os.path.dirname(vasplib.__file__),'../test/vasp/selective_BN_POSCAR'))
        self.assertEqual(p.lattice_flag, [])
        
        p.write_POSCAR(os.path.join(os.path.dirname(vasplib.__file__),'../test/vasp/BN_POSCAR'))

