import os
import unittest
import vasplib
from vasplib.output.xdatcar import Xdatcar
import numpy as np


class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        x = Xdatcar(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/XDATCAR'))
        s = x.structure(2)
        self.assertEqual(s.elements, ['Co', 'S'])
        self.assertTrue(np.allclose(s.atoms[0]['coords'][0], np.array([0.50000000, 0.50000000, 0.53429442])))

        x2 = Xdatcar(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/XDATCAR2'))
        s = x2.structure(1)
        self.assertTrue(np.allclose(s.lattice[0], np.array([5.506401, 0.000000, 0.000000])))