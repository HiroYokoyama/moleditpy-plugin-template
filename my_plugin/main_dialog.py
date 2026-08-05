"""Example dialog.

Kept deliberately small: a text field, a live preview and a save button, wired
the way the host expects (settings round-trip, project marked modified, no
modal dialogs during construction).
"""

from __future__ import annotations

import os

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
)


class MyPluginDialog(QDialog):
    def __init__(
        self,
        parent=None,
        persistent_settings=None,
        get_molecule=None,
        mark_modified=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("My Plugin")
        self.resize(640, 480)

        self.persistent_settings = persistent_settings if persistent_settings is not None else {}
        self.get_molecule = get_molecule
        self.mark_modified = mark_modified
        self._updating = False

        layout = QVBoxLayout(self)

        box = QGroupBox("Settings")
        form = QFormLayout(box)
        self.greeting_edit = QLineEdit()
        form.addRow("Greeting:", self.greeting_edit)
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 20)
        form.addRow("Repeat:", self.repeat_spin)
        layout.addWidget(box)

        self.summary_label = QLabel("-")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("Courier New", 9))
        layout.addWidget(self.preview, 1)

        buttons = QDialogButtonBox()
        self.save_button = buttons.addButton("Save...", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Close)
        self.save_button.clicked.connect(self.save_text)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)

        self.greeting_edit.textChanged.connect(self.update_preview)
        self.repeat_spin.valueChanged.connect(self.update_preview)

        self.apply_settings(self.persistent_settings)

    # -- settings ---------------------------------------------------------

    def apply_settings(self, settings) -> None:
        settings = settings or {}
        self._updating = True
        try:
            self.greeting_edit.setText(str(settings.get("greeting", "Hello")))
            self.repeat_spin.setValue(int(settings.get("repeat", 1)))
        finally:
            self._updating = False
        self.update_preview()

    def read_settings(self) -> dict:
        return {
            "greeting": self.greeting_edit.text(),
            "repeat": self.repeat_spin.value(),
        }

    # -- preview ----------------------------------------------------------

    def build_text(self) -> str:
        settings = self.read_settings()
        return "\n".join([settings["greeting"]] * max(1, int(settings["repeat"]))) + "\n"

    def update_preview(self, *_args) -> None:
        if self._updating:
            return
        self.persistent_settings.update(self.read_settings())
        if self.mark_modified is not None:
            try:
                self.mark_modified()
            except Exception:  # pragma: no cover - host API guard
                pass

        mol = self.get_molecule() if self.get_molecule is not None else None
        if mol is None:
            self.summary_label.setText("No molecule is loaded.")
        else:
            self.summary_label.setText(f"{mol.GetNumAtoms()} atoms in the current molecule.")
        self.preview.setPlainText(self.build_text())

    # -- output -----------------------------------------------------------

    def save_text(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save", "output.txt", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return
        try:
            # newline="\n" keeps the file identical on every platform.
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(self.build_text())
        except OSError as exc:
            QMessageBox.critical(self, "My Plugin", f"Could not write the file:\n{exc}")
            return
        QMessageBox.information(self, "My Plugin", f"Wrote\n{os.path.abspath(path)}")
