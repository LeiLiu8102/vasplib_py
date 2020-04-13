import os
import unittest
import vasplib
from vasplib.vasp.incar import Incar
import copy

class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        incar = Incar()
        incar.from_file(os.path.join(os.path.dirname(vasplib.__file__),'../test/vasp/INCAR'))
        self.assertEqual(incar.get_attr("EDIFF"), "1.0E-6")
        # How to copy an Incar object
        incar_copy = copy.deepcopy(incar)
        
        incar.update({"ENCUT": '500'})
        incar.remove("MAGMOM")
        incar.write_file(os.path.join(os.path.dirname(vasplib.__file__),'../test/vasp/INCAR2'))

