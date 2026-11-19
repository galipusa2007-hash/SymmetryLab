"""Быстрый независимый 3D-компонент: интерактивность выполняется в браузере.

Поворот камеры, масштаб и изменение хода операции не запускают Streamlit заново.
"""
from pathlib import Path
import json

import numpy as np
import streamlit.components.v1 as components

from symmetry.progression import OperationProgress
from symmetry.operations import SymmetryOperations
from visualization.molecule_viewer import MoleculeViewer, atom_label


class InteractiveMoleculeViewer:
    TEMPLATE = Path(__file__).parent / 'assets' / 'viewer.html'

    @staticmethod
    def payload(molecule, operation):
        source = molecule.get_coordinates()
        frames = []
        for p in range(101):
            coords, caption = OperationProgress.coordinates(molecule, operation, p / 100)
            frames.append({'coords': np.asarray(coords).round(7).tolist(), 'caption': caption})
        final = SymmetryOperations.apply(source, operation.matrix)
        visible_motion = bool(np.any(np.linalg.norm(final - source, axis=1) > 1e-8))
        axis = getattr(operation, 'axis', None)
        normal = getattr(operation, 'normal', None)
        return {
            'atoms': molecule.atoms,
            'labels': [atom_label(a, i) for i, a in enumerate(molecule.atoms)],
            'bonds': [list(b) for b in molecule.bonds],
            'original': source.tolist(),
            'frames': frames,
            'hasMotion': visible_motion,
            'operation': {'name': operation.name, 'kind': operation.kind,
                          'axis': None if axis is None else np.asarray(axis).tolist(),
                          'normal': None if normal is None else np.asarray(normal).tolist()},
            'colors': MoleculeViewer.COLORS,
            'limit': MoleculeViewer.LIMIT,
        }

    @classmethod
    def render(cls, molecule, operation, height=660):
        data = json.dumps(cls.payload(molecule, operation), ensure_ascii=False)
        data = data.replace('</', '<\\/')
        markup = cls.TEMPLATE.read_text(encoding='utf-8').replace('/*__SYMMETRY_DATA__*/null', data)
        components.html(markup, height=height, scrolling=False)
