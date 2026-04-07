"""Shared utility helpers for flex-jason."""

from __future__ import annotations

import copy
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

# ---------------------------------------------------------------------------
# Pipeline  –  structured dict wrapper for the agent pipeline state
# ---------------------------------------------------------------------------
# The pipeline object passed between agent stages has three top-level
# sections: datasets, variables, and programs.  Each section maps a
# user-chosen name to a dict whose shape is defined by the corresponding
# YAML schema file in  agent/schemas/.
#
# Usage:
#     p = Pipeline()                       # empty pipeline
#     p = Pipeline.from_yaml("state.yaml") # load existing state
#
#     p.add_dataset("DM")
#     p["datasets"]["DM"]["description"] = "Demographics"
#
#     p.remove_variable("OLD_VAR")
#
#     p.dataset_keys()   # dict_keys(["DM"])
#     p.to_dict()        # plain dict, ready for save_json_as_yaml()
# ---------------------------------------------------------------------------

_SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "agent" / "schemas"

_SECTION_SCHEMA_FILE = {
    "datasets": _SCHEMAS_DIR / "dataset.yaml",
    "variables": _SCHEMAS_DIR / "variable.yaml",
    "programs": _SCHEMAS_DIR / "program.yaml",
}


def _load_schema(section: str) -> dict:
    """Return a fresh copy of the schema template for *section*."""
    return load_yaml_as_json(_SECTION_SCHEMA_FILE[section])


class Pipeline:
    """Thin wrapper around the three-section pipeline dict.

    Provides named helpers for adding / removing / inspecting entries
    while keeping the underlying data as plain dicts (JSON-serialisable).
    """

    _SECTIONS = ("datasets", "variables", "programs")

    # -- construction --------------------------------------------------------

    def __init__(self, data: dict | None = None):
        if data is None:
            self._data: dict = {s: {} for s in self._SECTIONS}
        else:
            self._data = data
            for s in self._SECTIONS:
                self._data.setdefault(s, {})

    @classmethod
    def from_yaml(cls, path: Path | str) -> Pipeline:
        """Deserialise a Pipeline from a YAML file."""
        return cls(load_yaml_as_json(path))

    # -- dict-like access ----------------------------------------------------

    def __getitem__(self, key: str) -> dict:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    # -- per-section key / value helpers -------------------------------------

    def dataset_keys(self):
        return self._data["datasets"].keys()

    def dataset_values(self):
        return self._data["datasets"].values()

    def dataset_items(self):
        return self._data["datasets"].items()

    def variable_keys(self):
        return self._data["variables"].keys()

    def variable_values(self):
        return self._data["variables"].values()

    def variable_items(self):
        return self._data["variables"].items()

    def program_keys(self):
        return self._data["programs"].keys()

    def program_values(self):
        return self._data["programs"].values()

    def program_items(self):
        return self._data["programs"].items()

    # -- mutators ------------------------------------------------------------

    def _add(self, section: str, name: str, **overrides) -> dict:
        if name in self._data[section]:
            raise KeyError(f"{section} already contains '{name}'")
        entry = _load_schema(section)
        entry.update(overrides)
        self._data[section][name] = entry
        return entry

    def _remove(self, section: str, name: str) -> dict:
        return self._data[section].pop(name)

    def add_dataset(self, name: str, **overrides) -> dict:
        return self._add("datasets", name, **overrides)

    def remove_dataset(self, name: str) -> dict:
        return self._remove("datasets", name)

    def add_variable(self, name: str, **overrides) -> dict:
        return self._add("variables", name, **overrides)

    def remove_variable(self, name: str) -> dict:
        return self._remove("variables", name)

    def add_program(self, name: str, **overrides) -> dict:
        return self._add("programs", name, **overrides)

    def remove_program(self, name: str) -> dict:
        return self._remove("programs", name)

    # -- serialisation -------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a deep copy of the underlying plain dict."""
        return copy.deepcopy(self._data)

    def save(self, path: Path | str) -> None:
        """Persist the pipeline to a YAML file."""
        save_json_as_yaml(self._data, path)

    # -- repr ----------------------------------------------------------------

    def __repr__(self) -> str:
        counts = ", ".join(
            f"{s}={len(self._data[s])}" for s in self._SECTIONS
        )
        return f"Pipeline({counts})"


# ---------------------------------------------------------------------------
# Settings  –  LLM accounts + input file paths for agent stages
# ---------------------------------------------------------------------------
# The Settings object is the second dict passed to every agent stage (alongside
# Pipeline).  It bundles:
#   - llm  : the active LLM account details (provider, model, key, …)
#   - files : a dict of user-supplied input file paths (specs, RAG docs, PDFs)
#
# On disk it lives at  assets/settings.yaml  and is loaded/saved automatically
# so it persists across application runs.
#
# Usage:
#     s = Settings()                        # loads from disk or creates empty
#     s = Settings.from_yaml("settings.yaml")
#
#     s.set_llm_account(provider="Anthropic (Claude API)", model="claude-sonnet-4-20250514", api_key="sk-…")
#     s.clear_llm_account()
#
#     s.add_file("/data/spec.xlsx")
#     s.remove_file("/data/spec.xlsx")
#     s.list_files()
# ---------------------------------------------------------------------------

_LLM_SCHEMA_FILE = _SCHEMAS_DIR / "llm_account.yaml"

_SETTINGS_DEFAULT_PATH = Path(__file__).resolve().parents[1] / "assets" / "settings.yaml"


def _load_llm_schema() -> dict:
    """Return a fresh empty LLM account dict from the YAML template."""
    return load_yaml_as_json(_LLM_SCHEMA_FILE)


class Settings:
    """Persistent configuration passed to every agent stage.

    Wraps two concerns:
      - ``llm``   – the active LLM account (a flat dict matching llm_account.yaml)
      - ``files`` – a list of input file paths (stored as strings, exposed as Path objects)
    """

    def __init__(self, data: dict | None = None, path: Path | str | None = None):
        self._path = Path(path) if path else _SETTINGS_DEFAULT_PATH
        if data is None:
            self._data: dict = {"llm": _load_llm_schema(), "files": []}
        else:
            self._data = data
            self._data.setdefault("llm", _load_llm_schema())
            self._data.setdefault("files", [])

    @classmethod
    def from_yaml(cls, path: Path | str) -> Settings:
        """Load settings from a YAML file."""
        p = Path(path)
        if p.is_file():
            return cls(load_yaml_as_json(p), path=p)
        return cls(path=p)

    @classmethod
    def load(cls) -> Settings:
        """Load from the default location (assets/settings.yaml)."""
        return cls.from_yaml(_SETTINGS_DEFAULT_PATH)

    # -- LLM account ---------------------------------------------------------

    @property
    def llm(self) -> dict:
        """The active LLM account dict."""
        return self._data["llm"]

    def set_llm_account(self, **fields) -> None:
        """Update the active LLM account.  Only supplied keys are changed."""
        template = _load_llm_schema()
        for key, value in fields.items():
            if key not in template:
                raise KeyError(f"Unknown LLM account field: '{key}'")
            self._data["llm"][key] = value

    def clear_llm_account(self) -> None:
        """Reset the LLM account to an empty template."""
        self._data["llm"] = _load_llm_schema()

    @property
    def has_llm(self) -> bool:
        """True if a provider has been configured."""
        return bool(self._data["llm"].get("provider"))

    # -- files ---------------------------------------------------------------

    @property
    def files(self) -> list[Path]:
        """Return input file paths as Path objects."""
        return [Path(f) for f in self._data["files"]]

    def list_files(self) -> list[Path]:
        """Alias for ``files`` property."""
        return self.files

    def add_file(self, path: Path | str) -> None:
        """Add a file path (no-op if already present)."""
        s = str(path)
        if s not in self._data["files"]:
            self._data["files"].append(s)

    def remove_file(self, path: Path | str) -> None:
        """Remove a file path."""
        self._data["files"].remove(str(path))

    def clear_files(self) -> None:
        """Remove all file paths."""
        self._data["files"].clear()

    # -- dict-like access ----------------------------------------------------

    def __getitem__(self, key: str):
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    # -- serialisation -------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a deep copy of the underlying plain dict."""
        return copy.deepcopy(self._data)

    def save(self, path: Path | str | None = None) -> None:
        """Persist settings to YAML (default: assets/settings.yaml)."""
        save_json_as_yaml(self._data, Path(path) if path else self._path)

    # -- repr ----------------------------------------------------------------

    def __repr__(self) -> str:
        prov = self._data["llm"].get("provider") or "none"
        model = self._data["llm"].get("model") or "none"
        n = len(self._data["files"])
        return f"Settings(llm={prov}/{model}, files={n})"


# ---------------------------------------------------------------------------
# Spreadsheet / CSV reader  (returns Polars DataFrames)
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
