from typing import Dict, List

import streamlit as st

from generate_ppts import STYLE_PRESETS, build_presentation, load_outline

st.set_page_config(page_title="AIOT HW5 Q3", layout="wide")
st.title("HW5 Q3 — AI-Powered PPT Redesign")
st.write(
    "Generate two radically different decks for the Smart Campus pilot. "
    "ChatGPT supplied the layout, tone, and color palette, and `python-pptx` "
    "renders them reproducibly."
)

outline = load_outline()
slides_preview: List[Dict[str, str]] = [
    {"#": idx + 1, "type": slide["type"], "title": slide.get("title", "")}
    for idx, slide in enumerate(outline["slides"])
]
with st.expander("Slide outline", expanded=False):
    st.table(slides_preview)

col_a, col_b = st.columns(2)
for style_key, col in zip(["pulse_neon", "zen_canvas"], (col_a, col_b)):
    style = STYLE_PRESETS[style_key]
    with col:
        st.subheader(style["title"])
        st.markdown("Palette")
        palette_cols = st.columns(len(style["palette"]))
        for (name, rgb), color_col in zip(style["palette"].items(), palette_cols):
            color_col.markdown(
                f"<div style='padding:12px;background:rgb{rgb};border-radius:6px;text-align:center;color:#000;'>"
                f"{name}</div>",
                unsafe_allow_html=True,
            )
        if st.button(f"Generate {style['title']}", key=f"btn-{style_key}"):
            file_path = build_presentation(style_key, outline)
            deck_bytes = file_path.read_bytes()
            st.success(f"Generated {file_path.name}")
            st.download_button(
                label="Download deck",
                data=deck_bytes,
                file_name=file_path.name,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                key=f"dl-{style_key}",
            )

st.divider()
st.markdown(
    "**CLI shortcut** — `python3 aiot_hw5/Q3/generate_ppts.py --style pulse_neon` "
    "or replace with `zen_canvas` / `all` to regenerate files under `output/`."
)
st.info("Export PPT → PDF in PowerPoint if you need the report-ready artifact.")
