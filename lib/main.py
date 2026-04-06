from nicegui import ui
from pathlib import Path

from pages import filemgr, datasets, variables, derivations, codegen, englishgen, settings

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
DIVIDER_AFTER = {1, 4, 6}

# -- page renderers mapped by nav key ------------------------------------
PAGE_RENDERERS = {
    "filemgr":      lambda c: filemgr.render(c, pipeline),
    "datasets":     lambda c: datasets.render(c),
    "variables":    lambda c: variables.render(c),
    "derivations":  lambda c: derivations.render(c),
    "codegen":      lambda c: codegen.render(c),
    "descriptions": lambda c: englishgen.render(c),
    "settings":     lambda c: settings.render(c),
}


# -- single-page layout ---------------------------------------------------
@ui.page("/")
def index():
    ui.colors(primary="#C066B0")

    # content area — cleared and repopulated on navigation
    content = ui.column().classes("w-full")

    def navigate(key: str):
        content.clear()
        renderer = PAGE_RENDERERS.get(key, PAGE_RENDERERS["filemgr"])
        renderer(content)

    # sidebar — created once, never redrawn
    with ui.left_drawer(value=True, fixed=True, bordered=True).classes("bg-grey-2").style(
        "padding: 0;"
    ).props("width=175"):
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
    PAGE_RENDERERS["filemgr"](content)
