import os
import unittest
import vasplib
from vasplib.output.outcar import Outcar
import numpy as np


class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        x = Outcar(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/OUTCAR'))

        self.assertTrue(x.exists())
        self.assertEqual(x.get_species(), ["Pt", "N"])
        init_struct = x.initial_struct()
        self.assertAlmostEqual(init_struct.lattice[0, 0], 4.81014927)
        self.assertEqual(init_struct.atoms[0]['coords'][1, 2], 0.5)
        self.assertEqual(init_struct.atoms[0]['element'], 'Pt')
        self.assertEqual(init_struct.coord_type, 'direct')

        self.assertTrue(x.end_without_error())
        self.assertEqual(x.max_iteration(), (1, 23))
        self.assertEqual(x.ispin, 1)
        self.assertEqual(x.efermi, -2.9923)
        self.assertEqual(x.nkpts, 28)
        self.assertEqual(x.nbands, 32)
        self.assertAlmostEqual(x.bandgap()[0], 0.176)



        # test Outcar.struct_ionic_step(int)
        x = Outcar(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/OUTCAR2'))
        struct_10 = x.struct_ionic_step(10)
        self.assertAlmostEqual(struct_10.lattice[0, 0], 5.294306054)
        self.assertAlmostEqual(struct_10.atoms[1]['coords'][1, 0], 2.04820)

        # test Outcar.energy_ionic_step(i)
        self.assertAlmostEqual(x.energy_ionic_step(2), -26.85550843)

        # test Outcar.total_force_ionic_step(i)
        self.assertAlmostEqual(x.total_force_ionic_step(7)[5, 1], -0.016573)

