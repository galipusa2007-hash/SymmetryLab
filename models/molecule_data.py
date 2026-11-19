import numpy as np
from models.molecule import Molecule


class MoleculeData:
    """Идеализированные координаты (Å), согласованные с частями 1–2 РГР."""

    @staticmethod
    def titanium_dioxide():
        r = 1.62
        theta = np.radians(116 / 2)
        x, z = r * np.sin(theta), r * np.cos(theta)
        return Molecule(
            'TiO₂', ['Ti', 'O', 'O'],
            [[0, 0, 0], [x, 0, z], [-x, 0, z]],
            [(0, 1), (0, 2)], 'C2v'
        )

    @staticmethod
    def allene():
        # Ось z совпадает с C=C=C; две группы CH2 взаимно перпендикулярны.
        a, h, dz = 1.31, 0.96, 0.55
        return Molecule(
            'C₃H₄', ['C', 'C', 'C', 'H', 'H', 'H', 'H'],
            [[0, 0, 0], [0, 0, a], [0, 0, -a],
             [0, h, a + dz], [0, -h, a + dz],
             [h, 0, -a - dz], [-h, 0, -a - dz]],
            [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)],
            'D2d'
        )

    @staticmethod
    def borazine():
        # Плоское B-N-B-N-B-N кольцо в xy, начало координат — центр кольца.
        radius = 1.44
        atoms, coords, bonds = [], [], []
        for i in range(6):
            element = 'B' if i % 2 == 0 else 'N'
            theta = np.radians(90 + 60 * i)
            direction = np.array([np.cos(theta), np.sin(theta), 0.0])
            atoms.append(element)
            coords.append((radius * direction).tolist())
        for i in range(6):
            bonds.append((i, (i + 1) % 6))
        for i in range(6):
            theta = np.radians(90 + 60 * i)
            direction = np.array([np.cos(theta), np.sin(theta), 0.0])
            length = 1.19 if atoms[i] == 'B' else 1.00
            atoms.append('H')
            coords.append(((radius + length) * direction).tolist())
            bonds.append((i, 6 + i))
        return Molecule('B₃N₃H₆', atoms, coords, bonds, 'D3h')

    @staticmethod
    def get_all():
        return {
            'TiO₂': MoleculeData.titanium_dioxide(),
            'C₃H₄': MoleculeData.allene(),
            'B₃N₃H₆': MoleculeData.borazine(),
        }
