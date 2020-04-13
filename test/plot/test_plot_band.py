import os
import unittest
import vasplib
from vasplib.output.vaspxml import VaspXml
from vasplib.plot.plot_band import plot_electronic_band_structure
import numpy as np
import json


class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        pass
        # Test the plot of electronic band structure
        # with open(os.path.join(os.path.dirname(vasplib.__file__),'../test/plot/parm_electronic_band_structure_plot.json'), 'r') as fp:
        #     args = json.load(fp)

        # xml = VaspXml(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/vasprun.xml'))
        # args['ISPIN'] = xml.get_parameter('ISPIN')
        # args['NBANDS'] = xml.get_parameter("NBANDS")
        # args['NKPTS'] = xml.get_nkpts()
        # band_total = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/plot/band_total.dat'))
        # band_partial = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/plot/band_partial.dat'))
        # special_k = xml.get_high_symmetry_kpoints()

        # plot_electronic_band_structure(band_total, band_partial, special_k, args)
