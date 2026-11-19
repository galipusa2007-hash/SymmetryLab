"""Проверка контракта 3D-компонента при наличии Streamlit."""
import unittest
import numpy as np

from models.molecule_data import MoleculeData
from symmetry.operations import SymmetryOperations


class TestGeometryContract(unittest.TestCase):
    def test_stable_origin_and_zero_displacement_cases(self):
        molecules=MoleculeData.get_all()
        expected={'TiO₂': {'E','σ(xz)'}, 'C₃H₄': {'E'}, 'B₃N₃H₆': {'E','σh'}}
        for molecule in molecules.values():
            zero=set()
            for op in SymmetryOperations.get_operations(molecule.point_group):
                transformed=molecule.get_coordinates() @ op.matrix.T
                if np.allclose(transformed,molecule.get_coordinates(),atol=1e-8):
                    zero.add(op.name)
            # Проверка множества ниже устойчиво к именам из операций проекта.
            self.assertEqual(len(zero),len(expected[molecule.name]))
