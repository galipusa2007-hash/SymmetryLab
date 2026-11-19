import unittest
import numpy as np
from models.molecule_data import MoleculeData
from symmetry.operations import SymmetryOperations
from symmetry.progression import OperationProgress
from symmetry.permutation import atom_mapping


class TestProgression(unittest.TestCase):
    def test_endpoints(self):
        for molecule in MoleculeData.get_all().values():
            for op in SymmetryOperations.get_operations(molecule.point_group):
                start, _ = OperationProgress.coordinates(molecule, op, 0)
                final, _ = OperationProgress.coordinates(molecule, op, 1)
                expected = SymmetryOperations.apply(molecule.get_coordinates(), op.matrix)
                with self.subTest(molecule=molecule.name, operation=op.name):
                    self.assertTrue(np.allclose(start, molecule.get_coordinates()))
                    self.assertTrue(np.allclose(final, expected))

    def test_permutations_are_bijections(self):
        for molecule in MoleculeData.get_all().values():
            for op in SymmetryOperations.get_operations(molecule.point_group):
                perm = atom_mapping(molecule, op)
                self.assertEqual(set(perm), set(range(len(molecule.atoms))))
                self.assertEqual(set(perm.values()), set(range(len(molecule.atoms))))
