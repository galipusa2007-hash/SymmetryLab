"""Промежуточные координаты для демонстрации операций (не молекулярная динамика)."""
import numpy as np
from symmetry.operations import SymmetryOperations as Ops


class OperationProgress:
    @staticmethod
    def coordinates(molecule, operation, progress):
        p = np.clip(float(progress), 0.0, 1.0)
        original = molecule.get_coordinates()
        if operation.kind == 'identity':
            return original, 'Тождество: все атомы остаются на местах.'
        if operation.kind == 'rotation':
            matrix = Ops.rotation(operation.axis, operation.angle * p)
            return Ops.apply(original, matrix), f'Поворот: {p * operation.angle:.0f}° из {operation.angle:g}°.'
        if operation.kind == 'reflection':
            final = Ops.apply(original, operation.matrix)
            return (1 - p) * original + p * final, 'Геометрическая интерполяция отражения (не физическая траектория).'
        if operation.kind == 'improper':
            if p <= 0.5:
                fraction = p * 2
                matrix = Ops.rotation(operation.axis, operation.angle * fraction)
                return Ops.apply(original, matrix), f'Шаг 1/2: поворот на {fraction * operation.angle:.0f}°.'
            rotated = Ops.apply(original, Ops.rotation(operation.axis, operation.angle))
            reflected = Ops.apply(rotated, Ops.reflection(operation.normal))
            fraction = 2 * (p - 0.5)
            return ((1 - fraction) * rotated + fraction * reflected,
                    'Шаг 2/2: отражение после завершённого поворота (схематическая интерполяция).')
        if operation.kind == 'inversion':
            final = Ops.apply(original, operation.matrix)
            return (1 - p) * original + p * final, 'Схематическая интерполяция инверсии.'
        raise ValueError('Неизвестный тип операции')
