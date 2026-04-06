from nicegui import ui
from pathlib import Path

# -- shared pipeline state ------------------------------------------------
# Each stage reads from / writes to this dict.  Because NiceGUI runs in a
# single Python process the object is shared across page navigations.
pipeline = {}

# -- logo ------------------------------------------------------------------
img = Path(__file__).parent.parent / "assets" / "jason_logo.svg"
logo_svg = img.read_text()

# -- navigation definition ------------------------------------------------
NAV_ITEMS = [
    {"key": "filemgr",      "label": "File Manager",    "icon": "create_new_folder"},
    {"key": "datasets",     "label": "Datasets",        "icon": "library_books"},
    # --- divider ---
    {"key": "variables",    "label": "Variables",        "icon": "data_object"},
    {"key": "derivations",  "label": "Derivations",     "icon": "account_tree"},
    # --- divider ---
    {"key": "codegen",      "label": "Code Generation", "icon": "code"},
    {"key": "descriptions", "label": "Descriptions",    "icon": "chat_bubble_outline"},
    {"key": "settings",     "label": "Settings",        "icon": "settings"},
    # --- divider ---
]

# indices after which a divider is drawn (0-based)
DIVIDER_AFTER = {1, 3, 6}


# -- page content renderers -----------------------------------------------
# Each function receives the content container and populates it.
# Expand these as pipeline stages are built out.

def render_filemgr(container):
    with container:
        ui.label("File Manager").classes("text-h4 q-pa-md")


def render_datasets(container):
    with container:
        ui.label("Datasets").classes("text-h4 q-pa-md")


def render_variables(container):
    with container:
        ui.label("Variables").classes("text-h4 q-pa-md")


def render_derivations(container):
    with container:
        ui.label("Derivations").classes("text-h4 q-pa-md")


def render_codegen(container):
    with container:
        ui.label("Code Generation").classes("text-h4 q-pa-md")


def render_descriptions(container):
    with container:
        ui.label("Descriptions").classes("text-h4 q-pa-md")


def render_settings(container):
    with container:
        ui.label("Settings").classes("text-h4 q-pa-md")


PAGE_RENDERERS = {
    "filemgr": render_filemgr,
    "datasets": render_datasets,
    "variables": render_variables,
    "derivations": render_derivations,
    "codegen": render_codegen,
    "descriptions": render_descriptions,
    "settings": render_settings,
}


# -- single-page layout ---------------------------------------------------
@ui.page("/")
def index():
    ui.colors(primary="#C066B0")

    # content area — cleared and repopulated on navigation
    content = ui.column().classes("w-full")

    def navigate(key: str):
        content.clear()
        renderer = PAGE_RENDERERS.get(key, render_filemgr)
        renderer(content)

    # sidebar — created once, never redrawn
    with ui.left_drawer(value=True, fixed=True, bordered=True).classes("bg-grey-2").style(
        "padding: 0;"
    ).props("width=150"):
        ui.html(logo_svg).style("width: 130px; padding: 12px 8px 8px 8px;")

        for i, item in enumerate(NAV_ITEMS):
            if i in DIVIDER_AFTER:
                ui.separator().classes("my-2")

            link = ui.element("div").classes(
                "flex items-center gap-2 px-4 py-2 text-grey-8 hover:bg-grey-3 cursor-pointer"
            ).style("text-decoration: none;")
            with link:
                ui.icon(item["icon"]).classes("text-lg")
                ui.label(item["label"]).classes("text-sm")
            link.on("click", lambda _e, key=item["key"]: navigate(key))

    # render the default page
    render_filemgr(content)
