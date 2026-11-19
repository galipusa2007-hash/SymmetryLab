"""3D-визуализация с фиксированной системой координат и постоянным масштабом."""
import numpy as np
import plotly.graph_objects as go

CIRCLED_NUMBERS = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'


def atom_label(element, index):
    number = CIRCLED_NUMBERS[index] if index < len(CIRCLED_NUMBERS) else f'({index + 1})'
    return f'{element} {number}'


class MoleculeViewer:
    COLORS = {'Ti': '#8fa9b8', 'O': '#ef5753', 'C': '#64748b',
              'H': '#e2e8f0', 'B': '#f0a5b3', 'N': '#628bf0'}
    SIZES = {'Ti': 23, 'O': 19, 'C': 21, 'H': 12, 'B': 21, 'N': 21}
    LIMIT = 3.65
    CAMERA = dict(eye=dict(x=1.55, y=1.55, z=1.05),
                  up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0))

    @staticmethod
    def scene():
        def axis(title):
            return dict(title=title, range=[-MoleculeViewer.LIMIT, MoleculeViewer.LIMIT],
                        autorange=False, showgrid=True,
                        gridcolor='rgba(120,135,150,0.12)',
                        zeroline=False, showbackground=False,
                        tickfont=dict(size=10), nticks=5)
        return dict(xaxis=axis('X (Å)'), yaxis=axis('Y (Å)'), zaxis=axis('Z (Å)'),
                    aspectmode='cube', camera=MoleculeViewer.CAMERA,
                    dragmode='turntable', uirevision='camera-fixed-system')

    @staticmethod
    def add_world_axes(fig):
        extent = 3.3
        for i, (name, color) in enumerate((('X', '#e5a364'), ('Y', '#55c7b0'), ('Z', '#759ef8'))):
            start = np.zeros(3); end = np.zeros(3)
            start[i] = -extent; end[i] = extent
            fig.add_trace(go.Scatter3d(
                x=[start[0], end[0]], y=[start[1], end[1]], z=[start[2], end[2]],
                mode='lines', line=dict(color=color, width=4),
                hoverinfo='skip', showlegend=False))
            fig.add_trace(go.Scatter3d(
                x=[end[0]], y=[end[1]], z=[end[2]], mode='text',
                text=[name], textfont=dict(size=16, color=color),
                showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0], mode='markers',
            marker=dict(size=4, color='#f9d073', symbol='circle'),
            name='Начало координат O', hovertemplate='Начало координат (0, 0, 0)<extra></extra>'))

    @staticmethod
    def add_atoms(fig, molecule, coords, ghost=False):
        coords = np.asarray(coords, dtype=float)
        for i, j in molecule.bonds:
            fig.add_trace(go.Scatter3d(
                x=[coords[i, 0], coords[j, 0]],
                y=[coords[i, 1], coords[j, 1]],
                z=[coords[i, 2], coords[j, 2]],
                mode='lines', showlegend=False, hoverinfo='skip',
                line=dict(color='rgba(154,163,180,0.32)' if ghost else '#a3adba',
                          width=3 if ghost else 7)))
        for i, atom in enumerate(molecule.atoms):
            label = atom_label(atom, i)
            fig.add_trace(go.Scatter3d(
                x=[coords[i, 0]], y=[coords[i, 1]], z=[coords[i, 2]],
                mode='markers' if ghost else 'markers+text',
                marker=dict(size=(MoleculeViewer.SIZES.get(atom, 16) - 4) if ghost else MoleculeViewer.SIZES.get(atom, 16),
                            color='#94a3b8' if ghost else MoleculeViewer.COLORS.get(atom, '#aaa'),
                            opacity=0.23 if ghost else 1.0),
                text=None if ghost else [label], textposition='top center',
                textfont=dict(size=12, color='#e2e8f0'),
                showlegend=False, name=label,
                hoverinfo='skip' if ghost else None,
                hovertemplate=(f'<b>{label}</b><br>'
                               'X: %{x:.3f} Å<br>Y: %{y:.3f} Å<br>Z: %{z:.3f} Å'
                               '<extra></extra>') if not ghost else None))

    @staticmethod
    def create_figure(molecule, coordinates=None, operation=None,
                      show_element=True, show_ghost=False):
        coords = molecule.get_coordinates() if coordinates is None else np.asarray(coordinates, dtype=float)
        fig = go.Figure()
        MoleculeViewer.add_world_axes(fig)
        if show_ghost:
            MoleculeViewer.add_atoms(fig, molecule, molecule.get_coordinates(), ghost=True)
        if operation is not None and show_element:
            from visualization.symmetry_viewer import SymmetryViewer
            SymmetryViewer.add_element(fig, operation)
        MoleculeViewer.add_atoms(fig, molecule, coords, ghost=False)
        fig.update_layout(
            template='plotly_dark', paper_bgcolor='#0f1723',
            scene=dict(**MoleculeViewer.scene(), bgcolor='#0f1723'),
            height=610, margin=dict(l=0, r=0, b=0, t=15),
            showlegend=False, uirevision='stable-molecule-camera')
        return fig

    @staticmethod
    def create_comparison(molecule, transformed):
        """Совместимость с прежним интерфейсом: сравнение в двух независимых сценах."""
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=1, cols=2,
                            specs=[[{'type': 'scene'}, {'type': 'scene'}]],
                            subplot_titles=['Исходная модель', 'После преобразования'])
        for column, coordinates in ((1, molecule.get_coordinates()), (2, transformed)):
            temp = MoleculeViewer.create_figure(molecule, coordinates, show_element=False)
            for trace in temp.data:
                fig.add_trace(trace, row=1, col=column)
        fig.update_layout(scene=MoleculeViewer.scene(), scene2=MoleculeViewer.scene(),
                          height=570, template='plotly_dark', showlegend=False)
        return fig
