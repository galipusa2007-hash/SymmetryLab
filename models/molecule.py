import numpy as np

class Molecule:
    def __init__(self, name, atoms, coordinates, bonds, point_group):
        self.name = name
        self.atoms = list(atoms)
        self.coordinates = np.asarray(coordinates, dtype=float).copy()
        self.bonds = list(bonds)
        self.point_group = point_group
        if self.coordinates.shape != (len(self.atoms), 3):
            raise ValueError('Ожидается по три координаты на каждый атом')
        for i, j in self.bonds:
            if not (0 <= i < len(self.atoms) and 0 <= j < len(self.atoms)):
                raise ValueError('Некорректный индекс атома')

    def get_coordinates(self):
        return self.coordinates.copy()
