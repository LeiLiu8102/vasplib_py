import os
import unittest
import vasplib
from vasplib.core.structure import Structure
import numpy as np


class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        s = Structure()
        s.from_POSCAR(os.path.join(os.path.dirname(vasplib.__file__),'../test/core/POSCAR'))
        self.assertEqual(s.comment, "unknown system")
        self.assertEqual(s.coord_type, 'direct')
        self.assertAlmostEqual(s.density, 0.74885734428)

        s.direct_to_cart()
        s.cart_to_direct()
        self.assertTrue(np.allclose(s.atoms[0]['coords'][0], np.array([0.50000000, 0.50000000, 0.53429442])))
        self.assertTrue(np.allclose(s.cartesian_coords()[0], [2.7532005, 2.7532005, 9.61729956]))
        self.assertTrue(np.allclose(np.identity(3), np.dot(s.lattice, s.reciprocal_lattice)))
