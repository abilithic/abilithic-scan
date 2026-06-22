"""Main window. Thin UI: gathers input, runs the engine via a worker thread,
renders a ScanResult, and exports reports. No business logic lives here.
"""
from __future__ import annotations

import os

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QAction, QActionGroup, QIcon, QPixmap, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame, QTableView, QTextBrowser,
    QSplitter, QProgressBar, QPlainTextEdit, QFileDialog, QMessageBox, QDialog,
    QCheckBox, QDialogButtonBox, QHeaderView, QAbstractItemView, QTabWidget,
    QListWidget, QListWidgetItem)

from .. import __app_name__, __version__
from ..core.config import load_config, save_config
from ..core import paths
from ..core.normalize import validate_targets
from ..core.models import SEVERITY_ORDER, sev_rank
from ..engine import presets, locator
from ..engine.command_builder import ScanSpec, preview
from ..i18n import Translator
from .. import reports
from .theme import stylesheet, SEV_COLORS, ACCENT, MUTED
from .worker import ScanWorker
from .table_model import PortTableModel, PortProxy
from .nse_dialog import NSEDialog

AUTHOR = "Abil Khosim"
LINKEDIN_URL = "https://www.linkedin.com/in/abil-khosim-itsec/"
COPYRIGHT_YEAR = "2026"


def _logo(size):
    for rel in ("assets/abilithic-icon-256.png", "assets/abilithic-icon-1024.png",
                "assets/abilithic-mark-256.png"):
        p = paths.resource_path(rel)
        if os.path.exists(p):
            pm = QPixmap(p)
            if not pm.isNull():
                return pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return QPixmap()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.tr = Translator(self.cfg.language)
        self.result = None
        self.worker = None
        self.scanning = False
        self.nse_scripts = []
        self.nse_args = ""
        self._hint_widgets = {}

        ico = _logo(64)
        if not ico.isNull():
            self.setWindowIcon(QIcon(ico))

        self._build_ui()
        self._build_menu()
        self.apply_theme(self.cfg.theme)
        self.retranslate()
        self._refresh_command()
        self._check_environment()
        self.resize(1200, 780)

    # --------------------------------------------------------------------- #
    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 6)
        root.setSpacing(10)

        # ---- header ---- #
        head = QHBoxLayout()
        self.logo = QLabel()
        pm = _logo(46)
        if not pm.isNull():
            self.logo.setPixmap(pm)
        tbox = QVBoxLayout()
        self.title_lbl = QLabel(__app_name__)
        self.title_lbl.setStyleSheet(f"font-size:21px;font-weight:700;color:{ACCENT};")
        self.subtitle_lbl = QLabel("")
        self.subtitle_lbl.setStyleSheet(f"color:{MUTED};font-size:12px;")
        tbox.addWidget(self.title_lbl)
        tbox.addWidget(self.subtitle_lbl)
        head.addWidget(self.logo)
        head.addSpacing(8)
        head.addLayout(tbox)
        head.addStretch(1)
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Bahasa Indonesia", "id")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setCurrentIndex(0 if self.cfg.language == "id" else 1)
        self.lang_combo.currentIndexChanged.connect(self._on_language)
        self.theme_btn = QPushButton("◐")
        self.theme_btn.setObjectName("secondary")
        self.theme_btn.setFixedWidth(40)
        self.theme_btn.clicked.connect(self._toggle_theme)
        head.addWidget(self.lang_combo)
        head.addWidget(self.theme_btn)
        root.addLayout(head)

        # ---- controls row ---- #
        ctrl = QHBoxLayout()
        self.target_edit = QLineEdit()
        self.target_edit.returnPressed.connect(self.start_scan)
        self.profile_combo = QComboBox()
        for p in presets.profiles():
            self.profile_combo.addItem(self.tr(p["name_key"]), p["id"])
        self.profile_combo.currentIndexChanged.connect(self._on_profile)
        self.nse_btn = QPushButton("NSE…")
        self.nse_btn.setObjectName("secondary")
        self.nse_btn.clicked.connect(self._open_nse)
        self.scan_btn = QPushButton("")
        self.scan_btn.clicked.connect(self._scan_or_cancel)
        ctrl.addWidget(self.target_edit, 1)
        ctrl.addWidget(self.profile_combo)
        ctrl.addWidget(self.nse_btn)
        ctrl.addWidget(self.scan_btn)
        root.addLayout(ctrl)

        # ---- custom flags + command preview ---- #
        crow = QHBoxLayout()
        self.flags_edit = QLineEdit()
        self.flags_edit.textChanged.connect(self._refresh_command)
        crow.addWidget(self.flags_edit, 1)
        root.addLayout(crow)

        self.cmd_view = QLineEdit()
        self.cmd_view.setReadOnly(True)
        root.addWidget(self.cmd_view)

        # ---- banner ---- #
        self.banner = QLabel("")
        self.banner.setWordWrap(True)
        self.banner.setVisible(False)
        self.banner.setStyleSheet(
            "background:#2a2230;border:1px solid #ff9f43;border-radius:8px;"
            "padding:8px;color:#ffd166;")
        root.addWidget(self.banner)

        # ---- summary cards ---- #
        self.cards_row = QHBoxLayout()
        self.cards = {}
        for sev in reversed(SEVERITY_ORDER):
            card = QFrame()
            card.setObjectName("card")
            cl = QVBoxLayout(card)
            num = QLabel("0")
            num.setObjectName("cardNum")
            num.setStyleSheet(f"font-size:22px;font-weight:700;color:{SEV_COLORS[sev]};")
            num.setAlignment(Qt.AlignCenter)
            lbl = QLabel(sev)
            lbl.setObjectName("cardLbl")
            lbl.setAlignment(Qt.AlignCenter)
            cl.addWidget(num)
            cl.addWidget(lbl)
            self.cards[sev] = (num, lbl)
            self.cards_row.addWidget(card)
        root.addLayout(self.cards_row)

        # ---- main split: hosts | tabs ---- #
        split = QSplitter(Qt.Horizontal)
        self.host_list = QListWidget()
        self.host_list.currentRowChanged.connect(self._on_host_selected)
        split.addWidget(self.host_list)

        self.tabs = QTabWidget()
        # ports tab
        self.table = QTableView()
        self.model = PortTableModel(self.tr)
        self.proxy = PortProxy()
        self.proxy.setSourceModel(self.model)
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.tabs.addTab(self.table, "")
        # details / nse / priorities / log
        self.details = QTextBrowser()
        self.nse_view = QTextBrowser()
        self.prio_view = QTextBrowser()
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.tabs.addTab(self.prio_view, "")
        self.tabs.addTab(self.details, "")
        self.tabs.addTab(self.nse_view, "")
        self.tabs.addTab(self.log_view, "")
        split.addWidget(self.tabs)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setSizes([260, 940])
        root.addWidget(split, 1)

        # ---- progress ---- #
        prow = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.eta_lbl = QLabel("")
        self.eta_lbl.setStyleSheet(f"color:{MUTED};")
        prow.addWidget(self.progress, 1)
        prow.addWidget(self.eta_lbl)
        root.addLayout(prow)

        self.setCentralWidget(central)
        self.setStatusBar(self.statusBar())

    # --------------------------------------------------------------------- #
    def _build_menu(self):
        mb = self.menuBar()
        self._menus = {}
        self._actions = {}

        def act(key, hint_key, slot, shortcut=None, checkable=False):
            a = QAction(self.tr(key), self)
            if shortcut:
                a.setShortcut(shortcut)
            a.setCheckable(checkable)
            a.triggered.connect(slot)
            a.hovered.connect(lambda hk=hint_key: self.statusBar().showMessage(self.tr(hk)))
            self._actions[key] = (a, hint_key)
            return a

        m_file = mb.addMenu("")
        m_file.addAction(act("menu.file.new", "hint.file.new", self.new_scan, "Ctrl+N"))
        m_file.addAction(act("menu.file.open", "hint.file.open", self.open_result, "Ctrl+O"))
        m_file.addAction(act("menu.file.save", "hint.file.save", self.save_result, "Ctrl+S"))
        m_file.addSeparator()
        m_file.addAction(act("menu.file.import", "hint.file.import", self.import_targets))
        m_file.addSeparator()
        m_file.addAction(act("menu.file.export_excel", "hint.file.export_excel", lambda: self.export("xlsx")))
        m_file.addAction(act("menu.file.export_html", "hint.file.export_html", lambda: self.export("html")))
        m_file.addAction(act("menu.file.export_json", "hint.file.export_json", lambda: self.export("json")))
        m_file.addAction(act("menu.file.export_csv", "hint.file.export_csv", lambda: self.export("csv")))
        m_file.addSeparator()
        m_file.addAction(act("menu.file.exit", "hint.help.about", self.close))
        self._menus["menu.file"] = m_file

        m_scan = mb.addMenu("")
        self.act_start = act("menu.scan.start", "hint.scan.start", self.start_scan, "F5")
        self.act_cancel = act("menu.scan.cancel", "hint.scan.cancel", self.cancel_scan)
        m_scan.addAction(self.act_start)
        m_scan.addAction(self.act_cancel)
        m_scan.addSeparator()
        m_scan.addAction(act("menu.scan.nse", "hint.scan.nse", self._open_nse))
        self._menus["menu.scan"] = m_scan

        m_view = mb.addMenu("")
        m_view.addAction(act("menu.view.theme", "hint.view.theme", self._toggle_theme))
        self.act_learn = act("menu.view.learning", "hint.view.learning", self._toggle_learning, checkable=True)
        self.act_learn.setChecked(self.cfg.learning_mode)
        m_view.addAction(self.act_learn)
        self._menus["menu.view"] = m_view

        m_tools = mb.addMenu("")
        m_tools.addAction(act("menu.tools.nmap", "hint.tools.nmap", self._show_nmap))
        m_tools.addAction(act("menu.tools.npcap", "hint.tools.npcap", self._show_npcap))
        self._menus["menu.tools"] = m_tools

        m_help = mb.addMenu("")
        m_help.addAction(act("menu.help.quickstart", "hint.help.quickstart", self._show_quickstart))
        m_help.addAction(act("menu.help.licenses", "hint.help.licenses", self._show_licenses))
        m_help.addAction(act("menu.help.disclaimer", "hint.help.disclaimer", self._show_disclaimer))
        m_help.addAction(act("menu.help.about", "hint.help.about", self._show_about))
        self._menus["menu.help"] = m_help

        # status-bar hints on hover for the input controls too
        self._install_hint(self.target_edit, "hint.target")
        self._install_hint(self.profile_combo, "hint.profile")
        self._install_hint(self.nse_btn, "hint.scan.nse")
        self._install_hint(self.flags_edit, "hint.custom_flags")
        self._install_hint(self.cmd_view, "hint.command")

    def _install_hint(self, widget, key):
        self._hint_widgets[widget] = key
        widget.installEventFilter(self)

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Enter and obj in self._hint_widgets:
            self.statusBar().showMessage(self.tr(self._hint_widgets[obj]))
        elif ev.type() == QEvent.Leave and obj in self._hint_widgets:
            self.statusBar().clearMessage()
        return super().eventFilter(obj, ev)

    # --------------------------------------------------------------------- #
    # Translation / theming
    # --------------------------------------------------------------------- #
    def retranslate(self):
        self.subtitle_lbl.setText(self.tr("app.subtitle"))
        self.target_edit.setPlaceholderText(self.tr("ui.target.ph"))
        self.flags_edit.setPlaceholderText(self.tr("ui.custom_flags"))
        self.nse_btn.setToolTip(self.tr("hint.scan.nse"))
        self.theme_btn.setToolTip(self.tr("hint.view.theme"))
        self._set_scan_button()
        # tabs
        self.tabs.setTabText(0, self.tr("tab.ports"))
        self.tabs.setTabText(1, self.tr("tab.priorities"))
        self.tabs.setTabText(2, self.tr("tab.details"))
        self.tabs.setTabText(3, self.tr("tab.nse"))
        self.tabs.setTabText(4, self.tr("tab.log"))
        # cards labels
        for sev, (num, lbl) in self.cards.items():
            lbl.setText(self.tr(f"severity.{sev}"))
        # menus
        for key, menu in self._menus.items():
            menu.setTitle(self.tr(key))
        for key, (a, hk) in self._actions.items():
            a.setText(self.tr(key))
        # profile names
        cur = self.profile_combo.currentData()
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for p in presets.profiles():
            self.profile_combo.addItem(self.tr(p["name_key"]), p["id"])
        idx = self.profile_combo.findData(cur)
        self.profile_combo.setCurrentIndex(max(0, idx))
        self.profile_combo.blockSignals(False)
        self.model.headerDataChanged.emit(Qt.Horizontal, 0, 5)
        if not self.scanning:
            self.statusBar().showMessage(self.tr("status.idle"))
        if self.result:
            self._render(self.result)

    def apply_theme(self, theme):
        self.cfg.theme = theme
        QApplication.instance().setStyleSheet(stylesheet(theme))

    def _toggle_theme(self):
        self.apply_theme("light" if self.cfg.theme == "dark" else "dark")
        save_config(self.cfg)

    def _toggle_learning(self):
        self.cfg.learning_mode = self.act_learn.isChecked()
        save_config(self.cfg)
        self._refresh_command()

    def _on_language(self):
        self.cfg.language = self.lang_combo.currentData()
        self.tr.set_language(self.cfg.language)
        save_config(self.cfg)
        self.retranslate()
        self._refresh_command()

    # --------------------------------------------------------------------- #
    # Command building / preview
    # --------------------------------------------------------------------- #
    def _current_spec(self) -> ScanSpec:
        valid, _ = validate_targets(self.target_edit.text())
        pid = self.profile_combo.currentData()
        prof = presets.profile_by_id(pid) or {}
        flags = [f for f in self.flags_edit.text().split(" ") if f]
        return ScanSpec(
            targets=valid or (["<target>"] if not self.target_edit.text() else []),
            preset_args=list(prof.get("args", [])),
            nse=list(self.nse_scripts),
            nse_args=self.nse_args,
            extra_flags=flags,
        )

    def _refresh_command(self):
        spec = self._current_spec()
        nmap_name = "nmap"
        self.cmd_view.setText(preview(spec, nmap_name))

    def _on_profile(self):
        self._refresh_command()
        pid = self.profile_combo.currentData()
        prof = presets.profile_by_id(pid) or {}
        self.statusBar().showMessage(self.tr(prof.get("hint_key", "")))

    def _open_nse(self):
        dlg = NSEDialog(self.tr, self.nse_scripts, self.nse_args, self)
        if dlg.exec() == QDialog.Accepted:
            self.nse_scripts, self.nse_args = dlg.selection()
            self._refresh_command()

    # --------------------------------------------------------------------- #
    # Scan lifecycle
    # --------------------------------------------------------------------- #
    def _scan_or_cancel(self):
        if self.scanning:
            self.cancel_scan()
        else:
            self.start_scan()

    def start_scan(self):
        valid, invalid = validate_targets(self.target_edit.text())
        if not valid:
            QMessageBox.warning(self, __app_name__, self.tr("hint.target"))
            return
        if invalid:
            QMessageBox.warning(self, __app_name__,
                                self.tr("hint.target") + "\n\n" + ", ".join(invalid))

        pid = self.profile_combo.currentData()
        prof = presets.profile_by_id(pid) or {}
        intrusive = prof.get("intrusive") or any(
            x in ("vuln", "exploit", "dos", "brute", "intrusive", "fuzzer")
            for x in self.nse_scripts)

        if not self._consent(intrusive):
            return

        spec = self._current_spec()
        spec.targets = valid
        self.new_scan(keep_inputs=True)
        self.scanning = True
        self._set_scan_button()
        self.statusBar().showMessage(self.tr("status.scanning"))
        self.progress.setValue(0)

        self.worker = ScanWorker(spec, self.cfg, self.tr, profile_id=pid)
        self.worker.log.connect(self._on_log)
        self.worker.progress.connect(lambda d, t: self.progress.setValue(min(100, d)))
        self.worker.eta.connect(self._on_eta)
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def cancel_scan(self):
        if self.worker:
            self.worker.cancel()
            self._on_log("WARN", self.tr("log.cancelled"))

    def _consent(self, intrusive):
        if self.cfg.consent_remember and not intrusive:
            return True
        box = QMessageBox(self)
        box.setWindowTitle(self.tr("consent.title"))
        text = self.tr("consent.body")
        if intrusive:
            text += "\n\n⚠ " + self.tr("consent.intrusive")
        box.setText(text)
        yes = box.addButton(self.tr("consent.agree"), QMessageBox.AcceptRole)
        box.addButton(self.tr("consent.cancel"), QMessageBox.RejectRole)
        box.exec()
        return box.clickedButton() == yes

    def _on_log(self, level, msg):
        self.log_view.appendPlainText(f"[{level}] {msg}")

    def _on_eta(self, pct, remaining):
        self.progress.setValue(int(pct))
        if remaining > 0:
            mm, ss = divmod(int(remaining), 60)
            self.eta_lbl.setText(f"ETA {mm:02d}:{ss:02d}")

    def _on_finished(self, result):
        self.result = result
        self.scanning = False
        self._set_scan_button()
        self.progress.setValue(100)
        self.eta_lbl.setText("")
        m = result.scan_meta
        s = result.summary or {}
        if m.error == "nmap_not_found":
            self._show_banner(self.tr("banner.no_nmap"))
        self.statusBar().showMessage(self.tr("status.done").format(
            s=m.duration_s, hosts=s.get("hosts_up", 0), ports=s.get("open_ports", 0)))
        self._render(result)

    def _on_failed(self, err):
        self.scanning = False
        self._set_scan_button()
        QMessageBox.critical(self, __app_name__, self.tr("status.error") + "\n\n" + err)

    def _set_scan_button(self):
        if self.scanning:
            self.scan_btn.setText(self.tr("ui.cancel"))
            self.act_start.setEnabled(False)
            self.act_cancel.setEnabled(True)
        else:
            self.scan_btn.setText(self.tr("ui.start"))
            self.act_start.setEnabled(True)
            self.act_cancel.setEnabled(False)

    # --------------------------------------------------------------------- #
    # Rendering
    # --------------------------------------------------------------------- #
    def _render(self, result):
        self.model.set_result(result)
        self.table.sortByColumn(5, Qt.DescendingOrder)
        s = result.summary or {}
        by = s.get("by_severity", {})
        for sev, (num, lbl) in self.cards.items():
            num.setText(str(by.get(sev, 0)))
        # host list
        self.host_list.clear()
        for h in result.hosts:
            label = h.address or h.primary_name() or "?"
            item = QListWidgetItem(f"● {label}")
            item.setForeground(QColor(SEV_COLORS.get(h.risk_grade, "#8c97a8")))
            item.setData(Qt.UserRole, h)
            self.host_list.addItem(item)
        self._render_priorities(result)

    def _render_priorities(self, result):
        rows = []
        for p in result.priorities:
            color = SEV_COLORS.get(p.severity, "#8c97a8")
            fg = "#0c1118" if p.severity in ("MEDIUM", "LOW", "INFO") else "#fff"
            rows.append(
                f"<tr><td><span style='background:{color};color:{fg};padding:2px 8px;"
                f"border-radius:8px;font-weight:600'>{self.tr('severity.'+p.severity)}</span></td>"
                f"<td><b>{p.host}</b></td><td>{p.title}</td><td>{p.advice}</td></tr>")
        body = "".join(rows) or f"<tr><td>{self.tr('common.none')}</td></tr>"
        self.prio_view.setHtml(
            f"<h3 style='color:{ACCENT}'>{self.tr('tab.priorities')}</h3>"
            f"<table cellspacing='0' cellpadding='6' width='100%'>"
            f"<tr><th align='left'>{self.tr('col.criticality')}</th>"
            f"<th align='left'>{self.tr('col.host')}</th>"
            f"<th align='left'>{self.tr('col.problem')}</th>"
            f"<th align='left'>{self.tr('col.advice')}</th></tr>{body}</table>")

    def _on_host_selected(self, row):
        item = self.host_list.item(row)
        if not item:
            return
        h = item.data(Qt.UserRole)
        os_name = h.os_matches[0].name if h.os_matches else self.tr("common.none")
        lines = [f"<h3 style='color:{ACCENT}'>{h.address} "
                 f"<small style='color:{MUTED}'>{h.primary_name()}</small></h3>",
                 f"<b>{self.tr('col.os')}:</b> {os_name}<br>",
                 f"<b>{self.tr('col.exposure')}:</b> "
                 f"{self.tr('common.'+h.exposure) if h.exposure in ('public','internal') else h.exposure}<br>",
                 f"<b>{self.tr('col.risk')}:</b> "
                 f"<span style='color:{SEV_COLORS.get(h.risk_grade)}'>{self.tr('severity.'+h.risk_grade)}</span><hr>"]
        nse_lines = []
        for p in h.open_ports():
            why = "; ".join(c.reason for c in p.criticality.contributors)
            color = SEV_COLORS.get(p.criticality.severity)
            lines.append(
                f"<b>{p.portid}/{p.protocol}</b> — {p.service.name} {p.service.label()} "
                f"<span style='color:{color}'>[{self.tr('severity.'+p.criticality.severity)}]</span><br>"
                f"<span style='color:{MUTED}'>{why}</span><br>"
                f"<i>{p.criticality.advice}</i><br><br>")
            for sc in p.scripts:
                nse_lines.append(f"<b>{p.portid} · {sc.id}</b><pre>{sc.output}</pre>")
        self.details.setHtml("".join(lines))
        self.nse_view.setHtml("".join(nse_lines) or self.tr("common.none"))

    # --------------------------------------------------------------------- #
    # File ops
    # --------------------------------------------------------------------- #
    def new_scan(self, keep_inputs=False):
        self.result = None
        self.model.clear()
        self.host_list.clear()
        self.details.clear()
        self.nse_view.clear()
        self.prio_view.clear()
        self.log_view.clear()
        self.progress.setValue(0)
        self.eta_lbl.setText("")
        for sev, (num, lbl) in self.cards.items():
            num.setText("0")
        if not keep_inputs:
            self.target_edit.clear()
        self._hide_banner()

    def import_targets(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("menu.file.import"), "",
                                              "Text (*.txt);;All files (*.*)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                items = [ln.strip() for ln in fh if ln.strip()]
            self.target_edit.setText(" ".join(items))
            self._refresh_command()
        except Exception as e:
            QMessageBox.warning(self, __app_name__, str(e))

    def open_result(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("menu.file.open"),
                                              self.cfg.output_dir, "JSON (*.json)")
        if not path:
            return
        try:
            self.result = reports.load_json(path)
            self._render(self.result)
            self.statusBar().showMessage(os.path.basename(path))
        except Exception as e:
            QMessageBox.warning(self, __app_name__, str(e))

    def save_result(self):
        if not self._guard_result():
            return
        path, _ = QFileDialog.getSaveFileName(self, self.tr("menu.file.save"),
                                              os.path.join(self.cfg.output_dir, "scan.json"),
                                              "JSON (*.json)")
        if path:
            reports.save_json(self.result, path)
            self.statusBar().showMessage(path)

    def export(self, fmt):
        if not self._guard_result():
            return
        ext = {"xlsx": "Excel (*.xlsx)", "html": "HTML (*.html)",
               "json": "JSON (*.json)", "csv": "CSV (*.csv)"}[fmt]
        default = os.path.join(self.cfg.output_dir, f"abilithic-scan.{fmt}")
        path, _ = QFileDialog.getSaveFileName(self, self.tr(f"menu.file.export_{fmt}"),
                                              default, ext)
        if not path:
            return
        try:
            if fmt == "xlsx":
                reports.save_xlsx(self.result, path, self.tr)
            elif fmt == "html":
                reports.save_html(self.result, path, self.tr)
            elif fmt == "json":
                reports.save_json(self.result, path)
            else:
                reports.save_csv(self.result, path, self.tr)
            self.statusBar().showMessage(path)
        except Exception as e:
            QMessageBox.warning(self, __app_name__, str(e))

    def _guard_result(self):
        if not self.result or not self.result.hosts:
            QMessageBox.information(self, __app_name__, self.tr("status.idle"))
            return False
        return True

    # --------------------------------------------------------------------- #
    # Environment / dialogs
    # --------------------------------------------------------------------- #
    def _check_environment(self):
        if not locator.find_nmap():
            self._show_banner(self.tr("banner.no_nmap"))
        elif not locator.is_elevated():
            self._show_banner(self.tr("banner.no_admin"))
        elif not locator.has_npcap():
            self._show_banner(self.tr("banner.no_npcap"))

    def _show_banner(self, text):
        self.banner.setText("⚠  " + text)
        self.banner.setVisible(True)

    def _hide_banner(self):
        self.banner.setVisible(False)

    def _show_nmap(self):
        v = locator.nmap_version() or self.tr("banner.no_nmap")
        QMessageBox.information(self, self.tr("menu.tools.nmap"), v)

    def _show_npcap(self):
        ok = locator.has_npcap()
        QMessageBox.information(self, self.tr("menu.tools.npcap"),
                                self.tr("common.yes") if ok else self.tr("banner.no_npcap"))

    def _show_quickstart(self):
        QMessageBox.information(self, self.tr("menu.help.quickstart"), self.tr("quickstart.body"))

    def _show_licenses(self):
        QMessageBox.information(
            self, self.tr("menu.help.licenses"),
            "Abilithic Scan — MIT License © 2026 Abil Khosim.\n\n"
            "Nmap — Nmap Public Source License (NPSL).\n"
            "Npcap — Npcap License (redistribution requires permission).\n\n"
            "See THIRD-PARTY-LICENSES.md.")

    def _show_disclaimer(self):
        QMessageBox.warning(
            self, self.tr("menu.help.disclaimer"),
            "For authorized security testing and educational use only. "
            "Only scan systems you own or have explicit permission to test.")

    def _show_about(self):
        QMessageBox.about(
            self, self.tr("menu.help.about"),
            f"<b>{__app_name__}</b> v{__version__}<br>"
            f"{self.tr('app.subtitle')}<br><br>"
            f"by <b>{AUTHOR}</b> — {self.tr('about.role')}<br>"
            f"<a href='{LINKEDIN_URL}'>{LINKEDIN_URL}</a><br><br>"
            f"<i>{self.tr('about.tagline')} 🛡️</i><br>"
            f"© {COPYRIGHT_YEAR} {AUTHOR}. MIT License.")

    def closeEvent(self, ev):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(3000)
        save_config(self.cfg)
        super().closeEvent(ev)


def main():
    import sys
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
