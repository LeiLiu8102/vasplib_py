from vasplib.analysis.build import Build
from vasplib.core.structure import Structure
import unittest
import os
import vasplib
import numpy as np
import copy

class TestPeriodicTableClass(unittest.TestCase):

    def test(self):
        s = Build()
        s.from_POSCAR(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/POSCAR'))
        location0 = copy.deepcopy(s.atoms_flat[0])

        # test Build.permute_atom in place
        s.permute_atom(0, [0, 0.1, 0.2])
        location0_altered = s.atoms_flat[0]
        self.assertTrue(np.allclose(location0['coord'] + [0, 0.1, 0.2], location0_altered['coord']))

        # test Build.permute_atom out of place
        s1 = s.permute_atom(1, [0, 0.1, 0.2], inplace=False)
        self.assertAlmostEqual(s.atoms_flat[1]['coord'][2], 1.767174721)
        self.assertAlmostEqual(s1.atoms_flat[1]['coord'][2], 1.967174721)

        # test Build.supercell inplace, cartesional style
        s.supercell([2,2,1])
        self.assertTrue(np.allclose(s.lattice[0], [6.1473603, 0., 0,]))
        self.assertTrue(np.allclose(s.atoms_flat[-1]['coord'], [1.53683856, 4.43647595, 1.76717472]))

        # test Build.supercell inplace, direct style
        sd = Build()
        sd.from_POSCAR(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/POSCAR_direct.vasp'))
        sd.supercell([2,2,1])
        self.assertAlmostEqual(sd.atoms_flat[-1]['coord'][0], 0.66666649)

        # test Build.supercell out of place, cart style
        s.from_POSCAR(os.path.join(os.path.dirname(vasplib.__file__),'../test/analysis/POSCAR'))
        s2 = s.supercell([2,2,1], inplace = False)
        self.assertAlmostEqual(s.atoms_flat[1]['coord'][2], 1.767174721)
        self.assertTrue(np.allclose(s2.atoms_flat[-1]['coord'], [1.53683856, 4.43647595, 1.76717472]))
