"""SymmetryLab — интерактивная лаборатория симметрии молекул."""
from pathlib import Path
import numpy as np
import streamlit as st

from content.descriptions import MOLECULE_CONTEXT, describe
from content.research_tab import show_research
from models.molecule_data import MoleculeData
from symmetry.operations import SymmetryOperations
from symmetry.permutation import atom_mapping
from symmetry.validator import SymmetryValidator
from visualization.molecule_viewer import atom_label
from visualization.interactive_viewer import InteractiveMoleculeViewer

st.set_page_config(page_title='SymmetryLab | Молекулярная симметрия', page_icon='⚛️', layout='wide', initial_sidebar_state='collapsed')
stylesheet = (Path(__file__).parent / 'content' / 'site_theme.css').read_text(encoding='utf-8')
st.markdown(f'<style>{stylesheet}</style>', unsafe_allow_html=True)

MOLECULES = MoleculeData.get_all()
GROUP_HTML = {'C2v': 'C<sub>2v</sub>', 'D2d': 'D<sub>2d</sub>', 'D3h': 'D<sub>3h</sub>'}


def group_markup(text):
    return (str(text).replace('C₂ᵥ', 'C<sub>2v</sub>')
            .replace('D₂d', 'D<sub>2d</sub>')
            .replace('D₃ₕ', 'D<sub>3h</sub>'))


def choose_operation(value):
    st.session_state.operation = value


def changed_molecule():
    st.session_state.operation = 'E'


def operation_catalog(operations):
    cols = st.columns(4, gap='small')
    for index, op in enumerate(operations):
        with cols[index % 4]:
            st.button(op.name, key=f'op_{index}', use_container_width=True,
                      type='primary' if st.session_state.operation == op.name else 'secondary',
                      on_click=choose_operation, args=(op.name,))


def explain_model(molecule, operation):
    info = MOLECULE_CONTEXT[molecule.name]
    explanation = describe(molecule, operation)
    with st.expander('Почему так выбрана система координат?', expanded=False):
        st.markdown('**Начало координат и направления осей**')
        st.write(info['origin'])
        st.markdown('**Обоснование**')
        st.write(info['why'])
    with st.expander('Математика операции и химический смысл', expanded=False):
        st.markdown(f'**{operation.name} — математическое описание**')
        st.write(explanation['math'])
        st.write(explanation['movement'])
        st.markdown('**Химическая интерпретация**')
        st.markdown(group_markup(explanation['chemistry']), unsafe_allow_html=True)
        st.markdown('**Матрица преобразования**')
        st.code(np.array2string(operation.matrix, precision=3, suppress_small=True), language='text')


def lab():
    if 'operation' not in st.session_state:
        st.session_state.operation = 'E'

    select_col, count_col = st.columns([3, 2], gap='large')
    with select_col:
        name = st.selectbox('Молекула', list(MOLECULES), key='molecule', on_change=changed_molecule)
    molecule = MOLECULES[name]
    operations = SymmetryOperations.get_operations(molecule.point_group)
    with count_col:
        a, b, c = st.columns(3)
        a.metric('Атомы', len(molecule.atoms))
        b.markdown('<div class="group-card"><div class="group-heading">Группа</div>'
                   f'<div class="group-value">{GROUP_HTML[molecule.point_group]}</div></div>',
                   unsafe_allow_html=True)
        c.metric('Операции', len(operations))

    st.markdown('<p class="section-intro">' + group_markup(MOLECULE_CONTEXT[molecule.name]['geometry']) + '</p>', unsafe_allow_html=True)
    st.markdown('#### Выберите операцию')
    operation_catalog(operations)
    operation = next((op for op in operations if op.name == st.session_state.operation), operations[0])
    st.divider()

    viewer, details = st.columns([1.85, 1], gap='large')
    with viewer:
        InteractiveMoleculeViewer.render(molecule, operation, height=665)
    with details:
        st.subheader(operation.name)
        st.write(describe(molecule, operation)['movement'])
        mapping = atom_mapping(molecule, operation)
        moved = [(atom_label(molecule.atoms[i], i), atom_label(molecule.atoms[j], j))
                 for i, j in mapping.items() if i != j]
        if moved:
            pairs = ', '.join(f'{src} → позиция {dst}' for src, dst in moved[:5])
            if len(moved) > 5:
                pairs += f' и ещё {len(moved)-5}'
            st.caption('Перестановки: ' + pairs)
        else:
            st.caption('После операции каждый атом остаётся в своей позиции.')
        final = SymmetryOperations.apply(molecule.get_coordinates(), operation.matrix)
        if SymmetryValidator.validate(molecule, final):
            st.success('Совпадение подтверждено')
        else:
            st.error('Проверка совпадения не пройдена')
        explain_model(molecule, operation)

    with st.expander('Данные и результаты проверки', expanded=False):
        st.write(MOLECULE_CONTEXT[molecule.name]['model'])
        source = molecule.get_coordinates()
        target = SymmetryOperations.apply(source, operation.matrix)
        rows = []
        for i, atom in enumerate(molecule.atoms):
            rows.append({'Атом': atom_label(atom, i), 'X (Å)': round(source[i,0],3),
                         'Y (Å)': round(source[i,1],3), 'Z (Å)': round(source[i,2],3),
                         'X′ (Å)': round(target[i,0],3), 'Y′ (Å)': round(target[i,1],3),
                         'Z′ (Å)': round(target[i,2],3)})
        st.dataframe(rows, hide_index=True, use_container_width=True)
        checks = [SymmetryValidator.validate(molecule, SymmetryOperations.apply(source, op.matrix)) for op in operations]
        st.markdown(f'{sum(checks)} из {len(checks)} операций группы {GROUP_HTML[molecule.point_group]} подтверждены.', unsafe_allow_html=True)


def main():
    st.markdown('''<section class="hero"><div class="eyebrow">МОЛЕКУЛЯРНАЯ СИММЕТРИЯ • ИНТЕРАКТИВНО</div>
    <h1>SymmetryLab</h1></section>''', unsafe_allow_html=True)
    # Удаляем нативную подсказку `st.iframe` над 3D-областью.
    # Сохраняем доступное имя через aria-label.
    st.html("""<script>
    (() => {
      const clean = () => document.querySelectorAll('iframe[title="st.iframe"]').forEach(frame => {
        frame.setAttribute('aria-label', 'Интерактивная трёхмерная модель молекулы');
        frame.removeAttribute('title');
      });
      clean();
      const observer = new MutationObserver(clean);
      observer.observe(document.body, {childList:true, subtree:true, attributes:true, attributeFilter:['title']});
    })();
    </script>""", unsafe_allow_javascript=True)
    lab_tab, documents_tab = st.tabs(['⚛ 3D-лаборатория', '▤ Материалы РГР'])
    with lab_tab:
        lab()
    with documents_tab:
        show_research()


if __name__ == '__main__':
    main()
