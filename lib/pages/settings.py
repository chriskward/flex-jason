from pathlib import Path

from nicegui import ui

from utils import save_json_as_yaml, load_yaml_as_json

# ---------------------------------------------------------------------------
# LLM Account Settings Page
# ---------------------------------------------------------------------------
# Stores up to 6 LLM provider accounts.  Each account is represented as a
# horizontal strip that starts grey ("Set Account") and turns green once
# configured.  A radio-style checkbox group selects the *active* account.
# Settings are persisted to assets/llm_accounts.yaml.
# ---------------------------------------------------------------------------

PROVIDER_OPTIONS = [
    "Anthropic (Claude API)",
    "AWS Bedrock",
    "OpenRouter",
    "OpenAI",
    "Azure OpenAI",
    "Custom / Other",
]

NUM_SLOTS = 6

_SETTINGS_FILE = Path(__file__).resolve().parents[2] / "assets" / "llm_accounts.yaml"

_ACCOUNT_KEYS = [
    "provider", "account_name", "api_key", "base_url", "model",
    "aws_access_key_id", "aws_secret_access_key", "aws_region",
    "azure_api_version", "azure_deployment",
]


def _make_empty_account():
    """Return a blank account dict."""
    return {k: "" for k in _ACCOUNT_KEYS}


def _load_settings():
    """Load accounts and active index from disk. Returns (accounts, active_index)."""
    if _SETTINGS_FILE.is_file():
        try:
            data = load_yaml_as_json(_SETTINGS_FILE)
            saved = data.get("accounts", [])
            accounts = []
            for i in range(NUM_SLOTS):
                acct = _make_empty_account()
                if i < len(saved):
                    for k in _ACCOUNT_KEYS:
                        acct[k] = saved[i].get(k, "")
                accounts.append(acct)
            return accounts, data.get("active_index", None)
        except (TypeError, KeyError):
            pass
    return [_make_empty_account() for _ in range(NUM_SLOTS)], None


def _save_settings(accounts, active_index):
    """Persist accounts and active index to disk."""
    data = {"accounts": accounts, "active_index": active_index}
    save_json_as_yaml(data, _SETTINGS_FILE)


def render(container):
    # -- local state (loaded from disk) -------------------------------------
    accounts, _saved_active = _load_settings()
    active_index = {"value": _saved_active}  # which slot is the active LLM account

    # references to dynamic UI elements per slot
    strip_refs = []   # the coloured strip element
    label_refs = []   # the label inside the strip
    btn_refs = []     # the +/x button
    cb_refs = []      # the checkbox

    # -- helpers ------------------------------------------------------------

    def _display_name(idx):
        acct = accounts[idx]
        if acct["provider"]:
            name = acct["account_name"] or acct["provider"]
            if acct["model"]:
                name += f"  ({acct['model']})"
            return name
        return "Set Account"

    def _is_configured(idx):
        return bool(accounts[idx]["provider"])

    def _refresh_strip(idx):
        configured = _is_configured(idx)
        strip = strip_refs[idx]
        label = label_refs[idx]
        btn = btn_refs[idx]
        cb = cb_refs[idx]

        # strip colour
        if configured:
            strip.classes(remove="bg-grey-3")
            strip.classes(add="bg-green-3")
        else:
            strip.classes(remove="bg-green-3")
            strip.classes(add="bg-grey-3")

        # label text & colour
        label.set_text(_display_name(idx))
        if configured:
            label.classes(remove="text-grey-5")
            label.classes(add="text-grey-9")
        else:
            label.classes(remove="text-grey-9")
            label.classes(add="text-grey-5")

        # button icon
        btn.props(f'icon={"close" if configured else "add"}')

        # checkbox enabled state
        cb.set_enabled(configured)
        if not configured and active_index["value"] == idx:
            active_index["value"] = None
            cb.set_value(False)

    # -- modal dialog -------------------------------------------------------

    def _open_dialog(idx):
        acct = accounts[idx]
        # Working copy so Cancel doesn't mutate state
        draft = dict(acct)

        dlg = ui.dialog().props("persistent")
        with dlg, ui.card().classes("w-96"):
            ui.label("LLM Account Details").classes("text-h6 q-mb-sm")

            provider_select = ui.select(
                PROVIDER_OPTIONS,
                label="Provider",
                value=draft["provider"] or None,
            ).classes("w-full")

            account_name_input = ui.input(
                label="Account Name (optional)",
                value=draft["account_name"],
            ).classes("w-full")

            api_key_input = ui.input(
                label="API Key",
                value=draft["api_key"],
                password=True,
                password_toggle_button=True,
            ).classes("w-full")

            base_url_input = ui.input(
                label="Base URL (optional)",
                value=draft["base_url"],
                placeholder="e.g. https://openrouter.ai/api/v1",
            ).classes("w-full")

            model_input = ui.input(
                label="Model",
                value=draft["model"],
                placeholder="e.g. claude-sonnet-4-20250514",
            ).classes("w-full")

            # -- AWS Bedrock fields (shown conditionally) -------------------
            aws_section = ui.column().classes("w-full gap-0")
            with aws_section:
                ui.label("AWS Credentials").classes("text-subtitle2 q-mt-sm")
                aws_key_input = ui.input(
                    label="AWS Access Key ID",
                    value=draft["aws_access_key_id"],
                ).classes("w-full")
                aws_secret_input = ui.input(
                    label="AWS Secret Access Key",
                    value=draft["aws_secret_access_key"],
                    password=True,
                    password_toggle_button=True,
                ).classes("w-full")
                aws_region_input = ui.input(
                    label="AWS Region",
                    value=draft["aws_region"],
                    placeholder="e.g. us-east-1",
                ).classes("w-full")

            # -- Azure fields (shown conditionally) -------------------------
            azure_section = ui.column().classes("w-full gap-0")
            with azure_section:
                ui.label("Azure Settings").classes("text-subtitle2 q-mt-sm")
                azure_deployment_input = ui.input(
                    label="Azure Deployment Name",
                    value=draft["azure_deployment"],
                ).classes("w-full")
                azure_version_input = ui.input(
                    label="Azure API Version",
                    value=draft["azure_api_version"],
                    placeholder="e.g. 2024-02-01",
                ).classes("w-full")

            # -- conditional visibility -------------------------------------
            def _update_sections():
                prov = provider_select.value or ""
                aws_section.set_visibility(prov == "AWS Bedrock")
                azure_section.set_visibility(prov == "Azure OpenAI")
                if prov == "OpenRouter":
                    base_url_input.value = base_url_input.value or "https://openrouter.ai/api/v1"

            provider_select.on("update:model-value", lambda _: _update_sections())
            _update_sections()  # set initial visibility

            # -- dialog buttons ---------------------------------------------
            with ui.row().classes("w-full justify-end q-mt-md"):
                ui.button("Cancel", on_click=dlg.close).props("flat")

                def _on_ok():
                    acct["provider"] = provider_select.value or ""
                    acct["account_name"] = account_name_input.value or ""
                    acct["api_key"] = api_key_input.value or ""
                    acct["base_url"] = base_url_input.value or ""
                    acct["model"] = model_input.value or ""
                    acct["aws_access_key_id"] = aws_key_input.value or ""
                    acct["aws_secret_access_key"] = aws_secret_input.value or ""
                    acct["aws_region"] = aws_region_input.value or ""
                    acct["azure_deployment"] = azure_deployment_input.value or ""
                    acct["azure_api_version"] = azure_version_input.value or ""
                    _refresh_strip(idx)
                    _save_settings(accounts, active_index["value"])
                    dlg.close()

                ui.button("OK", on_click=_on_ok).props("unelevated color=primary")

        dlg.open()

    # -- delete handler -----------------------------------------------------

    def _delete_account(idx):
        accounts[idx] = _make_empty_account()
        _refresh_strip(idx)
        _save_settings(accounts, active_index["value"])

    # -- build the UI -------------------------------------------------------

    with container:
        ui.label("Settings").classes("text-h4 q-pa-md")

        for i in range(NUM_SLOTS):
            with ui.row().classes("w-full items-center q-px-md q-py-xs gap-2").style(
                "max-width: 700px;"
            ):
                # -- checkbox (active selector) ---
                cb = ui.checkbox(value=False).props("dense")
                cb.set_enabled(False)

                def _on_cb_change(e, slot=i):
                    if e.value:
                        # uncheck all others
                        active_index["value"] = slot
                        for j, other_cb in enumerate(cb_refs):
                            if j != slot:
                                other_cb.set_value(False)
                    else:
                        if active_index["value"] == slot:
                            active_index["value"] = None
                    _save_settings(accounts, active_index["value"])

                cb.on("update:model-value", _on_cb_change)
                cb_refs.append(cb)

                # -- strip (clickable row) ---
                strip = ui.row().classes(
                    "flex-grow items-center rounded q-px-md cursor-pointer bg-grey-3"
                ).style("height: 44px; min-width: 0;")

                with strip:
                    label = ui.label("Set Account").classes(
                        "flex-grow text-grey-5"
                    ).style("user-select: none;")

                    btn = ui.button(icon="add").props(
                        "flat dense round size=sm"
                    )

                strip_refs.append(strip)
                label_refs.append(label)
                btn_refs.append(btn)

                # clicking the strip opens the dialog (only if configured)
                strip.on(
                    "click",
                    lambda _e, slot=i: _open_dialog(slot) if _is_configured(slot) else None,
                )

                # +/x button handler
                def _btn_click(_e, slot=i):
                    if _is_configured(slot):
                        _delete_account(slot)
                    else:
                        _open_dialog(slot)

                btn.on("click", _btn_click)

        # -- restore persisted state after all slots are built ------------------
        for i in range(NUM_SLOTS):
            _refresh_strip(i)
            if active_index["value"] == i and _is_configured(i):
                cb_refs[i].set_value(True)
