"""Вкладка с оригинальными материалами расчётно-графической работы."""
from pathlib import Path
import base64
import html
import streamlit as st
import streamlit.components.v1 as components

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
    st.caption(f'{len(pages)} стр. · Страницы расположены друг под другом. '
               'Прокручивайте документ как обычную страницу.')

    # Dedicated fullscreen reader. It scrolls *inside* the fullscreen container,
    # unlike a fullscreen single-image lightbox that locks the entire document.
    fullscreen_pages = ''.join(
        f'<img src="data:image/webp;base64,{base64.b64encode(path.read_bytes()).decode("ascii")}" '
        f'alt="Страница {i}" loading="lazy">'
        for i, path in enumerate(pages, 1)
    )
    title_text = html.escape(f'Часть {number} · {title}')
    viewer_html = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box}}html,body{{margin:0;background:transparent;font-family:system-ui,-apple-system,sans-serif}}
#reader{{height:54px;background:transparent;overflow:hidden}}
#open{{padding:10px 15px;border:1px solid #bcd8ee;background:#fff;color:#245b93;
 border-radius:10px;cursor:pointer;font-size:13px}}
#toolbar{{display:none;position:sticky;top:0;z-index:2;background:#edf7ff;
 padding:12px 20px;border-bottom:1px solid #d9eafa;align-items:center;justify-content:space-between;gap:16px}}
#close{{border:1px solid #bcd8ee;background:white;padding:9px 13px;border-radius:9px;cursor:pointer}}
#pages{{display:none}}
#reader:fullscreen{{height:100vh;width:100vw;background:#e9f1f8;overflow-y:auto;overscroll-behavior:contain}}
#reader:fullscreen #open{{display:none}}
#reader:fullscreen #toolbar{{display:flex}}
#reader:fullscreen #pages{{display:block;padding:18px 12px 48px;max-width:1080px;margin:auto}}
#pages img{{display:block;width:100%;height:auto;margin:0 auto 17px;background:white;
 box-shadow:0 3px 18px #1e395029;border-radius:6px}}
</style></head><body><div id="reader">
<button id="open" type="button">⛶ Читать весь документ на полном экране</button>
<div id="toolbar"><strong>{title_text}</strong><button id="close" type="button">✕ Закрыть</button></div>
<div id="pages">{fullscreen_pages}</div></div>
<script>
const reader=document.getElementById('reader');
document.getElementById('open').onclick=async()=>{{
 try{{await reader.requestFullscreen();}}
 catch(e){{document.getElementById('open').textContent='Полноэкранный режим недоступен в браузере';}}
}};
document.getElementById('close').onclick=()=>{{if(document.fullscreenElement)document.exitFullscreen();}};
</script></body></html>"""
    components.html(viewer_html, height=54, scrolling=False)

    # Native Streamlit page scrolling: no page selector and no nested scroll frame.
    # Show every page in sequence; disable image lightbox where possible by rendering
    # them as ordinary HTML images, not clickable st.image widgets.
    for index, page_path in enumerate(pages, start=1):
        encoded = base64.b64encode(page_path.read_bytes()).decode('ascii')
        st.markdown(
            '<div class="document-page">'
            f'<img src="data:image/webp;base64,{encoded}" '
            f'alt="Часть {number}, страница {index}" loading="lazy" />'
            '</div>', unsafe_allow_html=True
        )





def show_research():
    """Показываем материалы РГР единым непрерывным документом без переключателя."""
    st.subheader('Теория и химический анализ')
    show_document(1, 'Теоретическая справка')
    st.divider()
    show_document(2, 'Химический анализ трёх молекул')
