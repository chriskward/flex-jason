import streamlit as st
from pathlib import Path
import base64

# encode the 

pages_dir = Path(__file__).parent / "pages"
img = Path(__file__).parent.parent / "assets" / "jason_logo.svg"

# encode jason the worm in b64
with open(img, "rb") as f:
    encoded = base64.b64encode(f.read()).decode()


st.markdown(f"""
<style>
[data-testid='stSidebarNav'] ul li:nth-child(2),
[data-testid='stSidebarNav'] ul li:nth-child(4),
[data-testid='stSidebarNav'] ul li:nth-child(7){{
    border-top: 1px solid rgba(0,0,0,0.15);
    margin-top: 0.5rem;
    padding-top: 0.5rem;
}}

[data-testid='stSidebar'] {{
    min-width: 200px;
    max-width: 200px;
}}

[data-testid='stSidebarHeader'] {{
    background-image: url("data:image/svg+xml;base64,{encoded}");
    background-repeat: no-repeat;
    background-size: 150px;
    background-position: left center;
    min-height: 200px;
}}
</style>
""", unsafe_allow_html=True)


pg = st.navigation([
     st.Page(str(pages_dir / "filemgr.py"), title="File Manager", icon=":material/create_new_folder:"),
     st.Page(str(pages_dir / "datasets.py"), title="Datasets", icon=":material/library_books:"),
     st.Page(str(pages_dir / "variables.py"), title="Variables", icon=":material/data_object:"),
     st.Page(str(pages_dir / "derivations.py"), title="Derivations", icon=":material/account_tree:"),
     st.Page(str(pages_dir / "codegen.py"), title="Code Generation", icon=":material/code:"),
     st.Page(str(pages_dir / "englishgen.py"), title="Descriptions", icon=":material/chat_bubble_outline:"),
     st.Page(str(pages_dir / "settings.py"), title="Settings", icon="⚙"),
])
pg.run()
