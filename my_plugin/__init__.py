"""Example MoleditPy plugin — rename this package and edit the metadata below.

Everything a plugin needs is here: the metadata the registry reads, an
``initialize(context)`` entry point, one menu action, and the three session
persistence handlers.
"""

import logging
import os

# --------------------------------------------------------------------------
# Registry metadata.  These constants are read by the plugin registry scripts,
# so keep the names exactly as they are.
# --------------------------------------------------------------------------

PLUGIN_NAME = "My Plugin"
PLUGIN_VERSION = "0.1.0"  # semver; the release tag must match (v0.1.0)
PLUGIN_AUTHOR = "Your Name"
PLUGIN_DESCRIPTION = "One sentence describing what the plugin does."
PLUGIN_CATEGORY = "Utility"
PLUGIN_TAGS = ["Utility"]  # keep it to one or two existing registry tags
PLUGIN_DEPENDENCIES = []  # pip packages beyond the host; PyQt6/rdkit/numpy are the host's
PLUGIN_SUPPORTED_MOLEDITPY_VERSION = ">=4.0.0, <5.0.0"
# Declare this only when the plugin genuinely cannot run somewhere:
# PLUGIN_SUPPORTED_OS = ["Windows", "macOS", "Linux", "WSL"]

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
WINDOW_ID = "my_plugin_dialog"

_context = None
_dialog_opened = False


def get_default_settings():
    return {"greeting": "Hello from My Plugin", "repeat": 1}


current_settings = get_default_settings()


def run(mw):
    """Open the dialog.  Called by the menu action registered in initialize()."""
    global _dialog_opened

    if _context is not None:
        mw = _context.get_main_window()

    from .main_dialog import MyPluginDialog

    # One dialog at a time: raise the existing one instead of opening a second.
    if _context is not None:
        existing = _context.get_window(WINDOW_ID)
        if existing is not None and existing.isVisible():
            existing.raise_()
            existing.activateWindow()
            return

    def _get_molecule():
        try:
            if _context is not None:
                return _context.current_molecule
        except Exception as exc:  # pragma: no cover - host API guard
            logging.warning("%s: could not read the molecule: %s", PLUGIN_NAME, exc)
        return getattr(mw, "current_mol", None)

    def _mark_modified():
        if _context is not None:
            try:
                _context.mark_project_modified()
            except Exception:  # pragma: no cover - host API guard
                pass

    _dialog_opened = True
    dlg = MyPluginDialog(
        parent=mw,
        persistent_settings=current_settings,
        get_molecule=_get_molecule,
        mark_modified=_mark_modified,
    )
    if _context is not None:
        _context.register_window(WINDOW_ID, dlg)
    dlg.show()


def initialize(context):
    """Entry point for the V4 plugin API.  Called once when MoleditPy starts."""
    global _context
    _context = context

    def show_dialog():
        run(context.get_main_window())

    # Pick ONE of these, matching what the plugin does:
    context.add_menu_action("Tools/My Plugin...", show_dialog)
    # context.add_export_action("My Format...", show_dialog)
    # context.add_analysis_tool("My Analysis...", show_dialog)
    # context.register_file_opener(".ext", open_callback)

    def save_state():
        # Returning {} until the dialog is used keeps unrelated projects clean.
        if not _dialog_opened:
            return {}
        return {"settings": dict(current_settings)}

    def load_state(data):
        if not isinstance(data, dict):
            return
        saved = data.get("settings")
        if isinstance(saved, dict):
            current_settings.update(saved)
            dlg = context.get_window(WINDOW_ID)
            if dlg is not None:
                try:
                    dlg.apply_settings(current_settings)
                except Exception as exc:  # pragma: no cover - host API guard
                    logging.warning("%s: could not apply loaded state: %s", PLUGIN_NAME, exc)

    def handle_reset():
        global _dialog_opened
        dlg = context.get_window(WINDOW_ID)
        if dlg is not None and dlg.isVisible():
            # Leave an open dialog alone: the user may still be editing.
            return
        current_settings.clear()
        current_settings.update(get_default_settings())
        _dialog_opened = False

    context.register_save_handler(save_state)
    context.register_load_handler(load_state)
    context.register_document_reset_handler(handle_reset)
