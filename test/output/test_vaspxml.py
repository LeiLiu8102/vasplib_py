import os
import unittest
import vasplib
from vasplib.output.vaspxml import VaspXml
import numpy as np


class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        myxml = VaspXml(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/vasprun.xml'))

        # test Vaspxml.get_parameter(param)
        self.assertEqual(myxml.get_parameter("IALGO"), 38)
        self.assertEqual(myxml.get_parameter("PREC"), 'accura')
        self.assertEqual(myxml.get_parameter("LWAVE"), False)

        self.assertEqual(myxml.get_species(), ['Co', 'Co', 'S', 'S', 'S', 'S'])
        self.assertEqual(myxml.get_nkpts(), 150)
        self.assertAlmostEqual(myxml.get_efermi(), -2.97398140)
        self.assertAlmostEqual(myxml.get_reclattice()[1,1], 0.18409695)
        self.assertTrue(np.allclose(myxml.get_kdistance()[:5], [0, 0.00323038, 0.00646077, 0.00969115, 0.0129215]))
        self.assertAlmostEqual(myxml.get_high_symmetry_kpoints()[-1], 0.502795)
        self.assertEqual(len(myxml.get_orbitals()), 9)

        # total_dos = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/dos.dat'))
        # self.assertTrue(np.allclose(myxml.get_total_dos(), total_dos))

        # dos_S_px = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/dos_S_px.dat'))
        # mydos_S_px = myxml.get_dos_element('S', 'px')
        # dos_S_px[3000:, 1] = -dos_S_px[3000:, 1]
        # self.assertTrue(np.allclose(dos_S_px, mydos_S_px))

        # dos_S = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/dos_S.dat'))
        # mydos_S = myxml.get_total_dos_element('S')
        # dos_S[3000:, 1] = -dos_S[3000:, 1]
        # self.assertTrue(np.allclose(dos_S, mydos_S))


        # band = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/band.dat'))
        # myband = myxml.get_electronic_band()
        # nkpts = myxml.get_nkpts()
        # self.assertTrue(np.allclose(myband[0:nkpts, 0:2], band[0:nkpts]))
        # self.assertTrue(np.allclose(myband[0:nkpts, -1], band[nkpts*31:nkpts*32, 1]))
        # self.assertTrue(np.allclose(myband[nkpts:nkpts*2, -1], band[nkpts*63:nkpts*64, 1]))

        # band_Co_dxy = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/band_Co_dxy.dat'))
        # myband_Co_dxy = myxml.get_electronic_band_element_orbit('Co', 'dxy')
        # self.assertTrue(np.allclose(band_Co_dxy, myband_Co_dxy))

        # band_S = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/output/band_S.dat'))
        # myband_S = myxml.get_electronic_band_element('S')
        # self.assertTrue(np.allclose(band_S, myband_S))
