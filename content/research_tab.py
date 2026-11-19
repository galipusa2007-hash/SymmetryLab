"""Вкладка с оригинальными материалами расчётно-графической работы."""
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]


def show_document(number: int, title: str):
    folder = ROOT / 'resources'
    # Если пользователь добавит оригинал части 1, его показываем и предлагаем для скачивания.
    original = folder / f'Часть {number}.docx'
    prepared = folder / 'Часть 1 — версия для сайта.docx'
    document = original if original.exists() else prepared if number == 1 else original

    st.markdown(f'#### Часть {number} · {title}')
    if document.exists():
        st.download_button(
            f'Скачать документ «{document.name}»',
            data=document.read_bytes(), file_name=document.name,
            mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            key=f'download_part_{number}'
        )

    pages = sorted((folder / f'part{number}').glob('page_*.webp'))
    if not pages:
        st.info('Предпросмотр пока недоступен. Документ можно скачать выше.')
        return
    page = st.select_slider(
        'Страница документа',
        options=list(range(1, len(pages) + 1)), value=1,
        format_func=lambda n: f'{n} / {len(pages)}',
        key=f'page_part_{number}'
    )
    st.image(str(pages[page - 1]), use_container_width=True)


def show_research():
    st.subheader('Теория и химический анализ')
    chapter = st.radio(
        'Раздел работы', ['Часть 1 · Теория', 'Часть 2 · Молекулы'],
        horizontal=True, label_visibility='collapsed'
    )
    if chapter.startswith('Часть 1'):
        show_document(1, 'Теоретическая справка')
    else:
        show_document(2, 'Химический анализ трёх молекул')
