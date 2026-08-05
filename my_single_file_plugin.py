"""A complete single-file MoleditPy plugin.

The package in `my_plugin/` is the shape to grow into; this is the shape most
plugins in the registry actually have. Everything lives in one module: metadata,
the entry point, and the dialog.

Copy this file to your plugins directory to try it, or use it as the starting
point for a single-file repository (see `examples/single_file/README.md`).
"""

import logging
import os

PLUGIN_NAME = "My Single File Plugin"
PLUGIN_VERSION = "0.1.0"
PLUGIN_AUTHOR = "Your Name"
PLUGIN_DESCRIPTION = "One sentence describing what the plugin does."
PLUGIN_CATEGORY = "Utility"
PLUGIN_TAGS = ["Utility"]
PLUGIN_DEPENDENCIES = []
PLUGIN_SUPPORTED_MOLEDITPY_VERSION = ">=4.0.0, <5.0.0"

WINDOW_ID = "my_single_file_plugin_dialog"

_context = None
_dialog_opened = False


def get_default_settings():
    return {"greeting": "Hello", "repeat": 1}


current_settings = get_default_settings()


def build_text(settings) -> str:
    """The plugin's actual work, kept out of the Qt code so it is easy to test."""
    greeting = str(settings.get("greeting", "Hello"))
    repeat = max(1, int(settings.get("repeat", 1)))
    return "\n".join([greeting] * repeat) + "\n"


def _make_dialog(parent):
    """Build the dialog lazily so importing the module never needs Qt."""
    from PyQt6.QtWidgets import (
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QLabel,
        QLineEdit,
        QSpinBox,
        QVBoxLayout,
    )

    class _Dialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle(PLUGIN_NAME)
            layout = QVBoxLayout(self)

            form = QFormLayout()
            self.greeting_edit = QLineEdit(str(current_settings.get("greeting", "Hello")))
            form.addRow("Greeting:", self.greeting_edit)
            self.repeat_spin = QSpinBox()
            self.repeat_spin.setRange(1, 20)
            self.repeat_spin.setValue(int(current_settings.get("repeat", 1)))
            form.addRow("Repeat:", self.repeat_spin)
            layout.addLayout(form)

            self.preview = QLabel()
            layout.addWidget(self.preview)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            buttons.rejected.connect(self.close)
            layout.addWidget(buttons)

            self.greeting_edit.textChanged.connect(self.refresh)
            self.repeat_spin.valueChanged.connect(self.refresh)
            self.refresh()

        def read_settings(self):
            return {
                "greeting": self.greeting_edit.text(),
                "repeat": self.repeat_spin.value(),
            }

        def apply_settings(self, settings):
            self.greeting_edit.setText(str(settings.get("greeting", "Hello")))
            self.repeat_spin.setValue(int(settings.get("repeat", 1)))

        def refresh(self, *_args):
            current_settings.update(self.read_settings())
            self.preview.setText(build_text(current_settings))
            if _context is not None:
                try:
                    _context.mark_project_modified()
                except Exception:  # pragma: no cover - host API guard
                    pass

    return _Dialog(parent)


def _open_dialog(mw):
    """Not named run(): the host would then add a second, duplicate menu entry."""
    global _dialog_opened

    if _context is not None:
        existing = _context.get_window(WINDOW_ID)
        if existing is not None and existing.isVisible():
            existing.raise_()
            existing.activateWindow()
            return

    _dialog_opened = True
    dlg = _make_dialog(mw)
    if _context is not None:
        _context.register_window(WINDOW_ID, dlg)
    dlg.show()


def initialize(context):
    global _context
    _context = context

    context.add_menu_action("Tools/My Single File Plugin...", lambda: _open_dialog(context.get_main_window()))

    def save_state():
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
            return
        current_settings.clear()
        current_settings.update(get_default_settings())
        _dialog_opened = False

    context.register_save_handler(save_state)
    context.register_load_handler(load_state)
    context.register_document_reset_handler(handle_reset)
