from nicegui import ui
from pathlib import Path

from pages import fileload, filesave, datasets, variables, dependencies, derivations, codegen, englishgen, settings, help

# -- shared pipeline state ------------------------------------------------
pipeline = {}

# -- logo ------------------------------------------------------------------
logo_path = Path(__file__).parent.parent / "assets" / "veramed.png"

# -- navigation definition ------------------------------------------------
# type: "heading" = non-clickable section heading, "page" = navigable page
NAV_ITEMS = [
    {"key": "filemgr",       "label": "File Manager",     "icon": "create_new_folder", "type": "heading"},
    {"key": "fileload",      "label": "Load",             "icon": "file_upload",       "type": "page", "indent": True},
    {"key": "filesave",      "label": "Save",             "icon": "file_download",     "type": "page", "indent": True},
    # --- divider ---
    {"key": "datasets",      "label": "Datasets",         "icon": "library_books",     "type": "page"},
    {"key": "variables",     "label": "Variables",         "icon": "data_object",       "type": "page"},
    {"key": "dependencies",  "label": "Dependencies",      "icon": "share",             "type": "page"},
    {"key": "derivations",   "label": "Derivations",       "icon": "account_tree",      "type": "page"},
    # --- divider ---
    {"key": "codegen",       "label": "Code Generation",   "icon": "code",              "type": "page"},
    {"key": "descriptions",  "label": "Descriptions",      "icon": "chat_bubble_outline","type": "page"},
    # --- divider ---
    {"key": "settings",      "label": "Settings",          "icon": "settings",          "type": "page"},
    {"key": "help",          "label": "Help",              "icon": "sentiment_very_dissatisfied", "type": "page"},
]

# indices before which a divider is drawn (0-based)
DIVIDER_BEFORE = {3, 7, 9}

# navigable pages only (for arrow key navigation)
PAGE_KEYS = [item["key"] for item in NAV_ITEMS if item["type"] == "page"]

# -- page renderers mapped by nav key ------------------------------------
PAGE_RENDERERS = {
    "fileload":     lambda c: fileload.render(c, pipeline),
    "filesave":     lambda c: filesave.render(c, pipeline),
    "datasets":     lambda c: datasets.render(c),
    "variables":    lambda c: variables.render(c),
    "dependencies": lambda c: dependencies.render(c),
    "derivations":  lambda c: derivations.render(c),
    "codegen":      lambda c: codegen.render(c),
    "descriptions": lambda c: englishgen.render(c),
    "settings":     lambda c: settings.render(c),
    "help":         lambda c: help.render(c),
}

# label lookup for page title display
PAGE_LABELS = {item["key"]: item["label"] for item in NAV_ITEMS}


# -- single-page layout ---------------------------------------------------
@ui.page("/")
def index():
    ui.colors(primary="#C066B0")

    # state
    current_page = {"key": "fileload"}
    sidebar_links: dict[str, ui.element] = {}

    # content area
    content = ui.column().classes("w-full")

    # title label reference (set after top bar is created)
    title_ref = {}

    def navigate(key: str):
        current_page["key"] = key
        content.clear()
        renderer = PAGE_RENDERERS.get(key, PAGE_RENDERERS["fileload"])
        renderer(content)
        # update title
        if "label" in title_ref:
            title_ref["label"].set_text(PAGE_LABELS.get(key, ""))
        # update sidebar highlight
        for k, link in sidebar_links.items():
            if k == key:
                link.classes(add="bg-grey-3", remove="")
            else:
                link.classes(remove="bg-grey-3")

    def navigate_prev():
        idx = PAGE_KEYS.index(current_page["key"]) if current_page["key"] in PAGE_KEYS else 0
        new_idx = max(0, idx - 1)
        navigate(PAGE_KEYS[new_idx])

    def navigate_next():
        idx = PAGE_KEYS.index(current_page["key"]) if current_page["key"] in PAGE_KEYS else 0
        new_idx = min(len(PAGE_KEYS) - 1, idx + 1)
        navigate(PAGE_KEYS[new_idx])

    # -- top bar (inside drawer area, aligned with logo) --------------------
    with ui.element("div").classes("fixed flex items-center").style(
        "background-color: #d5d5d5; height: 58px; left: 175px; top: 0; right: 0; z-index: 100;"
    ):
        ui.button(icon="keyboard_arrow_up", on_click=navigate_prev).props(
            "flat dense round"
        ).classes("text-grey-8 q-ml-sm")
        ui.button(icon="keyboard_arrow_down", on_click=navigate_next).props(
            "flat dense round"
        ).classes("text-grey-8")
        title_label = ui.label("Load").classes("text-subtitle1 text-grey-8 q-ml-sm")
        title_ref["label"] = title_label

    # push content below the top bar
    ui.element("div").style("height: 58px; flex-shrink: 0;")

    # -- sidebar -----------------------------------------------------------
    with ui.left_drawer(value=True, fixed=True, bordered=True).classes("bg-grey-2").style(
        "padding: 0;"
    ).props("width=175"):
        ui.image(str(logo_path)).style(
            "width: 100%; padding: 12px 16px 8px 16px; box-sizing: border-box;"
        )

        for i, item in enumerate(NAV_ITEMS):
            if i in DIVIDER_BEFORE:
                ui.separator().classes("my-2")

            if item["type"] == "heading":
                # non-clickable section heading
                with ui.element("div").classes(
                    "flex items-center gap-2 px-4 py-2 text-grey-8"
                ).style("text-decoration: none; cursor: default;"):
                    ui.icon(item["icon"]).classes("text-lg")
                    ui.label(item["label"]).classes("text-sm font-bold")
            else:
                # indent sub-items under a heading
                indent = "pl-8" if item.get("indent") else "px-4"
                link = ui.element("div").classes(
                    f"flex items-center gap-2 {indent} py-2 text-grey-8 hover:bg-grey-3 cursor-pointer"
                ).style("text-decoration: none;")
                with link:
                    ui.icon(item["icon"]).classes("text-lg")
                    ui.label(item["label"]).classes("text-sm")
                link.on("click", lambda _e, key=item["key"]: navigate(key))
                sidebar_links[item["key"]] = link

    # render default page and highlight it
    navigate("fileload")
