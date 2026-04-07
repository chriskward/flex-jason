import json
from nicegui import ui


def render(container, config, pipeline):
    stage_data = pipeline.get("derivations", {})

    with container:
        if not stage_data:
            ui.label("No derivations data yet. Complete the Dependencies stage first.").classes(
                "text-grey-6 q-pa-md"
            )
        else:
            ui.code(json.dumps(stage_data, indent=2, default=str)).classes("w-full q-pa-md")
