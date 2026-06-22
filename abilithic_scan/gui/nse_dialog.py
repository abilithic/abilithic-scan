"""NSE script picker: ready bundles, the 14 categories, and a custom box.
Every item carries a hint; dangerous categories are badged.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QWidget, QCheckBox,
    QLineEdit, QDialogButtonBox, QScrollArea, QPushButton)

from ..engine import presets

_SAFETY_BADGE = {
    "safe": ("✅", "#62d5b8"),
    "caution": ("⚠", "#ffd166"),
    "intrusive": ("⚠", "#ff9f43"),
    "dangerous": ("🛑", "#ff5c7a"),
}


class NSEDialog(QDialog):
    def __init__(self, tr, current: list, current_args: str = "", parent=None):
        super().__init__(parent)
        self.tr = tr
        self.setWindowTitle(tr("nse.title"))
        self.resize(560, 540)
        self._boxes: list = []

        root = QVBoxLayout(self)
        intro = QLabel(tr("nse.intro"))
        intro.setWordWrap(True)
        root.addWidget(intro)

        tabs = QTabWidget()
        tabs.addTab(self._bundles_tab(current), tr("nse.tab.bundles"))
        tabs.addTab(self._categories_tab(current), tr("nse.tab.categories"))
        tabs.addTab(self._custom_tab(current, current_args), tr("nse.tab.custom"))
        root.addWidget(tabs, 1)

        bb = QDialogButtonBox()
        ok = bb.addButton(tr("nse.ok"), QDialogButtonBox.AcceptRole)
        clear = bb.addButton(tr("nse.clear"), QDialogButtonBox.ResetRole)
        cancel = bb.addButton(tr("consent.cancel"), QDialogButtonBox.RejectRole)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        clear.clicked.connect(self._clear)
        root.addWidget(bb)

    def _scroll(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignTop)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setWidget(w)
        return sc, lay

    def _add_check(self, lay, expr, label, hint, safety, current):
        badge, color = _SAFETY_BADGE.get(safety, ("", "#8c97a8"))
        cb = QCheckBox(f"{badge}  {label}")
        cb.setStyleSheet(f"font-weight:600;")
        cb.setChecked(expr in current)
        cb._expr = expr
        self._boxes.append(cb)
        lay.addWidget(cb)
        h = QLabel("      " + hint)
        h.setWordWrap(True)
        h.setStyleSheet(f"color:#8c97a8;font-size:11px;")
        lay.addWidget(h)

    def _bundles_tab(self, current):
        sc, lay = self._scroll()
        for b in presets.nse_bundles():
            self._add_check(lay, b["expr"], b["id"].replace("_", " ").title(),
                            self.tr(b["hint_key"]), b.get("safety", "safe"), current)
        return sc

    def _categories_tab(self, current):
        sc, lay = self._scroll()
        for c in presets.nse_categories():
            self._add_check(lay, c["id"], c["id"],
                            self.tr(c["hint_key"]), c.get("safety", "safe"), current)
        return sc

    def _custom_tab(self, current, current_args):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(QLabel("--script"))
        self.custom_edit = QLineEdit()
        self.custom_edit.setPlaceholderText(self.tr("nse.custom.ph"))
        # prefill with any current expr that isn't a known bundle/category
        known = {b["expr"] for b in presets.nse_bundles()} | {c["id"] for c in presets.nse_categories()}
        leftover = [x for x in current if x not in known]
        if leftover:
            self.custom_edit.setText(",".join(leftover))
        lay.addWidget(self.custom_edit)
        lay.addSpacing(8)
        lay.addWidget(QLabel("--script-args"))
        self.args_edit = QLineEdit(current_args)
        self.args_edit.setPlaceholderText(self.tr("nse.args.ph"))
        lay.addWidget(self.args_edit)
        return w

    def _clear(self):
        for cb in self._boxes:
            cb.setChecked(False)
        self.custom_edit.clear()
        self.args_edit.clear()

    def selection(self):
        exprs = [cb._expr for cb in self._boxes if cb.isChecked()]
        custom = self.custom_edit.text().strip()
        if custom:
            exprs.extend([x.strip() for x in custom.split(",") if x.strip()])
        # de-duplicate, preserve order
        seen, out = set(), []
        for e in exprs:
            if e not in seen:
                seen.add(e)
                out.append(e)
        return out, self.args_edit.text().strip()
