import json
from nicegui import ui


def render(container, config, pipeline):
    stage_data = pipeline.get("codegen", {})

    with container:
        if not stage_data:
            ui.label("No code generation data yet. Complete the Derivations stage first.").classes(
                "text-grey-6 q-pa-md"
            )
        else:
            ui.code(json.dumps(stage_data, indent=2, default=str)).classes("w-full q-pa-md")
