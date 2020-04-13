from vasplib.analysis.chemenv import LocalEnv
from vasplib.core.structure import Structure
import unittest
import os
import vasplib
import numpy as np

class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        lenv = LocalEnv()
        lenv.from_POSCAR(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/POSCAR'))
        self.assertTrue(np.allclose([3.073680, 3.073680, 3.534349, 90.0, 90.0, 120.0],
                    lenv.lattice_constants))

        sites = lenv.periodic_sites(1, [-1.5, 1, -0.8, 1, 0, 1.6])
        self.assertTrue(np.allclose(sites[3], np.array([-1.33333301, 0.33333296, 1.5])))
        self.assertTrue(np.allclose(lenv.neighbors(2, 3)[5][2], 2.504412))

        neis = lenv.neighbors_shell(2, shell = 2)
        self.assertEqual(len(neis), 6)
        self.assertTrue(np.allclose(neis[0][2], 2.50441))

