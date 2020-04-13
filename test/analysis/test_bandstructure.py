import os
import unittest
import vasplib
from vasplib.output.vaspxml import VaspXml
from vasplib.analysis.bandstructure import Bandstructure
import numpy as np

class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        myxml = VaspXml(os.path.join(os.path.dirname(vasplib.__file__), '../test/analysis/WSeS.xml'))
        kpoints = myxml.get_kdistance()
        eigenvalues = myxml.get_electronic_band()[:, 1:]
        bs = Bandstructure(kpoints, eigenvalues)

        self.assertTrue(not bs.is_metal())

        # Test Bandstructure.get_band_gap()
        band_gap = bs.get_band_gap()
        self.assertAlmostEqual(band_gap['energy'], 1.6889)
        self.assertTrue(band_gap['direct'])
        self.assertEqual(band_gap['from'], (49, 8))
        self.assertEqual(band_gap['to'], (49, 9))

        # Test Bandstructure.get_ele_eff_mass(N)
        self.assertAlmostEqual(bs.get_elec_eff_mass(N = 4), 0.35987237)
        self.assertAlmostEqual(bs.get_hole_eff_mass(N = 4), -0.4769069)