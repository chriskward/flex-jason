import streamlit as st
from pathlib import Path

pages_dir = Path(__file__).parent / "pages"
img = Path(__file__).parent.parent / "assets" / "jason_logo.svg"

st.sidebar.image(str(img), width=150)
st.sidebar.markdown("---")

main_pages = [
    st.Page(str(pages_dir / "placeholder_1.py"), title="Placeholder 1"),
    st.Page(str(pages_dir / "placeholder_2.py"), title="Placeholder 2"),
    st.Page(str(pages_dir / "placeholder_3.py"), title="Placeholder 3"),
    st.Page(str(pages_dir / "placeholder_4.py"), title="Placeholder 4"),
    st.Page(str(pages_dir / "placeholder_5.py"), title="Placeholder 5"),
    st.Page(str(pages_dir / "placeholder_6.py"), title="Placeholder 6"),
]

settings_pages = [
    st.Page(str(pages_dir / "settings.py"), title="Settings", icon="⚙"),
]

pg = st.navigation({"Main": main_pages, "": settings_pages})
pg.run()
