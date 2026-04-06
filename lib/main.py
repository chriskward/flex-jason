from nicegui import ui, app
from pathlib import Path
import base64

# -- shared pipeline state ------------------------------------------------
# Each stage reads from / writes to this dict.  Because NiceGUI runs in a
# single Python process the object is shared across page navigations.
pipeline = {}

# -- logo ------------------------------------------------------------------
img = Path(__file__).parent.parent / "assets" / "jason_logo.svg"
with open(img, "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()
logo_data_uri = f"data:image/svg+xml;base64,{logo_b64}"

# -- navigation definition ------------------------------------------------
NAV_ITEMS = [
    {"path": "/",             "label": "File Manager",    "icon": "create_new_folder"},
    {"path": "/datasets",     "label": "Datasets",        "icon": "library_books"},
    # --- divider ---
    {"path": "/variables",    "label": "Variables",        "icon": "data_object"},
    {"path": "/derivations",  "label": "Derivations",     "icon": "account_tree"},
    # --- divider ---
    {"path": "/codegen",      "label": "Code Generation", "icon": "code"},
    {"path": "/descriptions", "label": "Descriptions",    "icon": "chat_bubble_outline"},
    {"path": "/settings",     "label": "Settings",        "icon": "settings"},
    # --- divider ---
]

# indices after which a divider is drawn (0-based)
DIVIDER_AFTER = {1, 3, 6}


def sidebar() -> None:
    """Render the shared sidebar with logo and navigation links."""
    with ui.left_drawer(value=True, fixed=True, bordered=True).classes("bg-white").style(
        "width: 200px; min-width: 200px; max-width: 200px; padding: 0;"
    ):
        # logo
        ui.image(logo_data_uri).style("width: 150px; padding: 16px 16px 8px 16px;")

        # nav links
        for i, item in enumerate(NAV_ITEMS):
            if i in DIVIDER_AFTER:
                ui.separator().classes("my-2")

            with ui.element("a").props(f'href="{item["path"]}"').classes(
                "flex items-center gap-2 px-4 py-2 no-underline text-grey-8 hover:bg-grey-2"
            ).style("text-decoration: none;"):
                ui.icon(item["icon"]).classes("text-lg")
                ui.label(item["label"]).classes("text-sm")


def page_layout(title: str):
    """Common page wrapper: header + sidebar + titled content area."""
    ui.colors(primary="#C066B0")
    with ui.header(elevated=True).classes("bg-white text-grey-9 q-py-xs").style("height: 48px;"):
        ui.label("Flexible Jason").classes("text-h6")
    sidebar()
    ui.label(title).classes("text-h4 q-pa-md")


# -- pages (stubs — each will grow into a pipeline stage) ------------------
@ui.page("/")
def page_filemgr():
    page_layout("File Manager")


@ui.page("/datasets")
def page_datasets():
    page_layout("Datasets")


@ui.page("/variables")
def page_variables():
    page_layout("Variables")


@ui.page("/derivations")
def page_derivations():
    page_layout("Derivations")


@ui.page("/codegen")
def page_codegen():
    page_layout("Code Generation")


@ui.page("/descriptions")
def page_descriptions():
    page_layout("Descriptions")


@ui.page("/settings")
def page_settings():
    page_layout("Settings")
