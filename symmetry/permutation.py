"""Соответствие атомов после операции: элемент и координаты должны совпадать."""
import numpy as np
from symmetry.operations import SymmetryOperations


def atom_mapping(molecule, operation, tolerance=1e-6):
    original = molecule.get_coordinates()
    transformed = SymmetryOperations.apply(original, operation.matrix)
    mapping = {}
    used = set()
    for i, element in enumerate(molecule.atoms):
        candidates = [j for j, other in enumerate(molecule.atoms)
                      if other == element and j not in used and
                      np.linalg.norm(transformed[i] - original[j]) < tolerance]
        if not candidates:
            raise ValueError(f'Атом {i} не совмещён ни с одним эквивалентным атомом')
        destination = candidates[0]
        used.add(destination)
        mapping[i] = destination
    return mapping
