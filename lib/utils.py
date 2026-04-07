"""Shared utility helpers for flex-jason."""

from pathlib import Path

import polars as pl
import yaml


# ---------------------------------------------------------------------------
# YAML ↔ dict  (human-readable JSON persistence)
# ---------------------------------------------------------------------------
# These two functions replace raw json.dumps / json.loads throughout the app
# so that configuration files are stored as readable YAML on disk while the
# application works with plain Python dicts (i.e. JSON-compatible objects).
#
# Usage – saving:
#     data = {"accounts": [...], "active_index": 2}
#     save_json_as_yaml(data, "assets/llm_accounts.yaml")
#
# Usage – loading:
#     data = load_yaml_as_json("assets/llm_accounts.yaml")
#     accounts = data["accounts"]
# ---------------------------------------------------------------------------


def save_json_as_yaml(data: dict, path: Path | str) -> None:
    """Serialise a JSON-compatible dict to a human-readable YAML file."""
    Path(path).write_text(
        yaml.dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def load_yaml_as_json(path: Path | str) -> dict:
    """Read a YAML file and return its contents as a Python dict (JSON-compatible)."""
    text = Path(path).read_text(encoding="utf-8")
    return yaml.safe_load(text) or {}


# ---------------------------------------------------------------------------
# Spreadsheet / CSV reader  (returns Polars DataFrames)
# ---------------------------------------------------------------------------
# Reads tabular data from a single file path.  Supports:
#   - Excel workbooks  (.xlsx, .xls, .xlsb)  — via the fastexcel / calamine engine
#   - OpenDocument      (.ods)                — via the fastexcel / calamine engine
#   - CSV               (.csv)                — via Polars' built-in CSV reader
#
# For workbook formats that may contain multiple sheets the function returns
# a dict mapping each sheet name to its Polars DataFrame.  For CSV files
# (which are inherently single-sheet) a dict with a single entry is returned,
# keyed by the filename stem.
#
# Usage – single-sheet workbook or CSV:
#     sheets = read_sheet("data/demographics.xlsx")
#     df = list(sheets.values())[0]          # grab the only DataFrame
#
# Usage – multi-sheet workbook:
#     sheets = read_sheet("data/study.xlsx")
#     for name, df in sheets.items():
#         print(f"Sheet '{name}': {df.shape}")
#
# Usage – with file manager pipeline paths:
#     for path in pipeline["selected_files"]:
#         sheets = read_sheet(path)
#         ...
#
# Requirements: pip install polars fastexcel
# ---------------------------------------------------------------------------

_SPREADSHEET_EXTS = {".xlsx", ".xls", ".xlsb", ".ods"}


def read_sheet(path: Path | str) -> dict[str, pl.DataFrame]:
    """Read a spreadsheet or CSV file and return a dict of sheet-name → DataFrame.

    For workbook formats every sheet is read.  For CSV a single entry is
    returned keyed by the file's stem (e.g. ``"demographics"``).

    Raises ``ValueError`` for unsupported file extensions.
    """
    p = Path(path)
    ext = p.suffix.lower()

    if ext == ".csv":
        return {p.stem: pl.read_csv(p)}

    if ext in _SPREADSHEET_EXTS:
        # Use calamine engine for broad format support (xlsx/xls/xlsb/ods)
        xl = pl.read_excel(p, engine="calamine", sheet_id=0)
        # sheet_id=0 returns a dict[str, DataFrame] of all sheets
        if isinstance(xl, dict):
            return xl
        # Defensive: if a single DataFrame is returned, wrap it
        return {p.stem: xl}

    raise ValueError(
        f"Unsupported file format '{ext}'. "
        f"Expected one of: .csv, {', '.join(sorted(_SPREADSHEET_EXTS))}"
    )
