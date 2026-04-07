"""Agent: Descriptions stage.

Accepts a config dict (files + LLM settings) and a pipeline dict
(accumulated processing state).  Returns an updated pipeline dict.

Can be run standalone:
    python -m agent.descriptions config.yaml pipeline.yaml
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from utils import load_yaml_as_json, save_json_as_yaml


def run(config: dict, pipeline: dict) -> dict:
    """Execute the Descriptions stage.

    Parameters
    ----------
    config : dict
        Contains ``selected_files`` (from Load) and ``llm`` settings (from Settings).
    pipeline : dict
        Accumulated pipeline state from previous stages.

    Returns
    -------
    dict
        Updated pipeline with a ``descriptions`` key added/modified.
    """
    pipeline.setdefault("descriptions", {})
    return pipeline


def main():
    parser = argparse.ArgumentParser(description="Run the Descriptions pipeline stage")
    parser.add_argument("config", help="Path to config YAML file")
    parser.add_argument("pipeline", help="Path to pipeline YAML file")
    parser.add_argument("-o", "--output", help="Output YAML path (default: overwrite pipeline)")
    args = parser.parse_args()

    config = load_yaml_as_json(args.config)
    pipeline = load_yaml_as_json(args.pipeline)

    pipeline = run(config, pipeline)

    out_path = args.output or args.pipeline
    save_json_as_yaml(pipeline, out_path)
    print(f"Pipeline written to {out_path}")


if __name__ == "__main__":
    main()
