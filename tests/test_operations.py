import unittest
import numpy as np
from models.molecule_data import MoleculeData
from symmetry.operations import SymmetryOperations
from symmetry.validator import SymmetryValidator
from content.descriptions import MOLECULE_CONTEXT, describe


class TestSymmetryOperations(unittest.TestCase):
    def test_all_operations(self):
        counts = {'C2v': 4, 'D2d': 8, 'D3h': 12}
        atom_counts = {'TiO₂': 3, 'C₃H₄': 7, 'B₃N₃H₆': 12}
        for molecule in MoleculeData.get_all().values():
            ops = SymmetryOperations.get_operations(molecule.point_group)
            self.assertEqual(len(ops), counts[molecule.point_group])
            self.assertEqual(len(molecule.atoms), atom_counts[molecule.name])
            for op in ops:
                with self.subTest(molecule=molecule.name, operation=op.name):
                    result = SymmetryOperations.apply(molecule.get_coordinates(), op.matrix)
                    self.assertTrue(SymmetryValidator.validate(molecule, result))
                    self.assertTrue(np.allclose(op.matrix.T @ op.matrix, np.eye(3), atol=1e-8))
                    self.assertTrue(describe(molecule, op)['chemistry'])

    def test_unique_operations(self):
        for molecule in MoleculeData.get_all().values():
            ops = SymmetryOperations.get_operations(molecule.point_group)
            for i in range(len(ops)):
                for j in range(i + 1, len(ops)):
                    self.assertFalse(np.allclose(ops[i].matrix, ops[j].matrix))

    def test_group_closure(self):
        for molecule in MoleculeData.get_all().values():
            ops = SymmetryOperations.get_operations(molecule.point_group)
            for left in ops:
                for right in ops:
                    product = left.matrix @ right.matrix
                    self.assertTrue(any(np.allclose(product, op.matrix, atol=1e-8) for op in ops))

    def test_identity_and_inverse(self):
        for molecule in MoleculeData.get_all().values():
            ops = SymmetryOperations.get_operations(molecule.point_group)
            for op in ops:
                self.assertTrue(any(np.allclose(op.matrix @ inv.matrix, np.eye(3), atol=1e-8) for inv in ops))

    def test_origin_and_geometry(self):
        molecules = MoleculeData.get_all()
        self.assertTrue(np.allclose(molecules['TiO₂'].coordinates[0], 0))
        self.assertTrue(np.allclose(molecules['C₃H₄'].coordinates[0], 0))
        self.assertTrue(np.allclose(np.mean(molecules['B₃N₃H₆'].coordinates[:6], axis=0), 0, atol=1e-8))
        self.assertEqual(len(MOLECULE_CONTEXT), 3)


if __name__ == '__main__':
    unittest.main()
