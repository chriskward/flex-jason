import json
from nicegui import ui


def render(container, config, pipeline):
    stage_data = pipeline.get("datasets", {})

    with container:
        if not stage_data:
            ui.label("No datasets data yet. Ensure files are loaded and settings are configured.").classes(
                "text-grey-6 q-pa-md"
            )
        else:
            ui.code(json.dumps(stage_data, indent=2, default=str)).classes("w-full q-pa-md")
