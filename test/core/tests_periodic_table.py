import unittest
from vasplib.core import periodic_table as pt

class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        element = pt.Element('H')
        self.assertAlmostEqual(element.get_attr("Atomic mass"), 1.00794)
        self.assertEqual(element.get_attr("Electronic structure"), "1s<sup>1</sup>")
        self.assertEqual(element.get_attr("ICSD oxidation states"), [1, -1])

        element = element.from_Z(11)
        self.assertEqual(element.symbol, 'Na')
        self.assertAlmostEqual(element.get_attr("Atomic orbitals")["1s"], -37.719975)