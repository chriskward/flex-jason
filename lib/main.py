import sys
from pathlib import Path

from nicegui import ui

from pages import fileload, filesave, datasets, variables, dependencies, derivations, codegen, englishgen, settings, help
from utils import Settings, Pipeline

# allow importing from repo root (for agent modules)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import datasets as agent_datasets
from agent import variables as agent_variables
from agent import dependencies as agent_dependencies
from agent import derivations as agent_derivations
from agent import codegen as agent_codegen
from agent import descriptions as agent_descriptions

# -- shared state ----------------------------------------------------------
# settings: LLM account + input file paths  (persistent across runs)
# pipeline: accumulated output from each stage, passed sequentially
settings_obj = Settings.load()
pipeline = {}

# -- logo ------------------------------------------------------------------
logo_path = Path(__file__).parent.parent / "assets" / "veramed.png"

# -- agent mapping ---------------------------------------------------------
# Maps sidebar keys to their agent module's run() function.
STAGE_AGENTS = {
    "datasets":     agent_datasets.run,
    "variables":    agent_variables.run,
    "dependencies": agent_dependencies.run,
    "derivations":  agent_derivations.run,
    "codegen":      agent_codegen.run,
    "descriptions": agent_descriptions.run,
}

# -- navigation definition ------------------------------------------------
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

DIVIDER_BEFORE = {3, 7, 9}

PAGE_KEYS = [item["key"] for item in NAV_ITEMS if item["type"] == "page"]

# -- page renderers mapped by nav key ------------------------------------
PAGE_RENDERERS = {
    "fileload":     lambda c: fileload.render(c, settings_obj),
    "filesave":     lambda c: filesave.render(c, pipeline),
    "datasets":     lambda c: datasets.render(c, settings_obj, pipeline),
    "variables":    lambda c: variables.render(c, settings_obj, pipeline),
    "dependencies": lambda c: dependencies.render(c, settings_obj, pipeline),
    "derivations":  lambda c: derivations.render(c, settings_obj, pipeline),
    "codegen":      lambda c: codegen.render(c, settings_obj, pipeline),
    "descriptions": lambda c: englishgen.render(c, settings_obj, pipeline),
    "settings":     lambda c: settings.render(c, settings_obj),
    "help":         lambda c: help.render(c),
}

PAGE_LABELS = {item["key"]: item["label"] for item in NAV_ITEMS}


# -- single-page layout ---------------------------------------------------
@ui.page("/")
def index():
    ui.colors(primary="#C066B0")

    current_page = {"key": "fileload"}
    sidebar_links: dict[str, ui.element] = {}

    content = ui.column().classes("w-full")
    title_ref = {}

    def navigate(key: str):
        current_page["key"] = key

        # If navigating to a stage page, run its agent first
        if key in STAGE_AGENTS:
            global pipeline
            pipeline = STAGE_AGENTS[key](settings_obj, pipeline)

        content.clear()
        renderer = PAGE_RENDERERS.get(key, PAGE_RENDERERS["fileload"])
        renderer(content)

        if "label" in title_ref:
            title_ref["label"].set_text(PAGE_LABELS.get(key, ""))

        for k, link in sidebar_links.items():
            if k == key:
                link.classes(add="bg-grey-3", remove="")
            else:
                link.classes(remove="bg-grey-3")

    def navigate_prev():
        idx = PAGE_KEYS.index(current_page["key"]) if current_page["key"] in PAGE_KEYS else 0
        navigate(PAGE_KEYS[max(0, idx - 1)])

    def navigate_next():
        idx = PAGE_KEYS.index(current_page["key"]) if current_page["key"] in PAGE_KEYS else 0
        navigate(PAGE_KEYS[min(len(PAGE_KEYS) - 1, idx + 1)])

    # -- top bar -----------------------------------------------------------
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
                with ui.element("div").classes(
                    "flex items-center gap-2 px-4 py-2 text-grey-8"
                ).style("text-decoration: none; cursor: default;"):
                    ui.icon(item["icon"]).classes("text-lg")
                    ui.label(item["label"]).classes("text-sm font-bold")
            else:
                indent = "pl-8" if item.get("indent") else "px-4"
                link = ui.element("div").classes(
                    f"flex items-center gap-2 {indent} py-2 text-grey-8 hover:bg-grey-3 cursor-pointer"
                ).style("text-decoration: none;")
                with link:
                    ui.icon(item["icon"]).classes("text-lg")
                    ui.label(item["label"]).classes("text-sm")
                link.on("click", lambda _e, key=item["key"]: navigate(key))
                sidebar_links[item["key"]] = link

    navigate("fileload")
