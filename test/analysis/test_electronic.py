import os
import unittest
import vasplib
from vasplib.analysis.electronic import analyze_electronic_property as AEP
from vasplib.output.vaspxml import VaspXml
import numpy as np
import json


class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        # this test is ommitted due to its requirement of long time
        pass
        # # Test the analysis on electronic density of states
        # with open(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/parm_electronic_dos.json'), 'r') as fp:
        #     args = json.load(fp)
        # AEP(args)

        # dos_analy = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/dos.dat'))

        # myxml = VaspXml(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/vasprun.xml'))
        # dos_xml = myxml.get_total_dos()
        # dos_xml = np.append(dos_xml, myxml.get_dos_element('Co', 'px'), axis = 0)
        # dos_xml = np.append(dos_xml, myxml.get_dos_element('Co', 'py'), axis = 0)
        # dos_xml = np.append(dos_xml, myxml.get_dos_element('S', 'px'), axis = 0)
        # dos_xml = np.append(dos_xml, myxml.get_total_dos_element('S'), axis = 0)

        # self.assertTrue(np.allclose(dos_analy, dos_xml))

        # # # Test the plot
        # with open(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/parm_electronic_dos_plot.json'), 'r') as fp:
        #     args = json.load(fp)
        # AEP(args)

        # # Test the analysis on electronic band structure
        # with open(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/parm_electronic_band_structure.json'), 'r') as fp:
        #     args = json.load(fp)
        # AEP(args)

        # band_total = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/band_total.dat'))
        # band_partial = np.loadtxt(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/band_partial.dat'))

        # xml = VaspXml(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/vasprun.xml'))
        # band_total_xml = xml.get_electronic_band()
        # self.assertTrue(np.allclose(band_total_xml, band_total))

        # band_Co_px_xml = xml.get_electronic_band_element_orbit('Co', 'px')
        # band_Co_py_xml = xml.get_electronic_band_element_orbit('Co', 'py')
        # band_S_xml = xml.get_electronic_band_element('S')
        # band_partial_xml = np.concatenate((band_Co_px_xml, band_Co_py_xml, band_S_xml), axis = 0)
        # self.assertTrue(np.allclose(band_partial_xml, band_partial))

        # # Test the plot of band structures
        # with open(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/parm_electronic_band_structure_plot.json'), 'r') as fp:
            # args = json.load(fp)
        # AEP(args)