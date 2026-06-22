"""QThread worker: runs the engine off the UI thread and marshals events as
Qt signals (delivered safely on the GUI thread). Engine never touches widgets.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal

from ..core.cancel import CancelToken
from ..engine import orchestrator


class _SignalSink(QObject):
    phase = Signal(str)
    progress = Signal(int, int)
    log = Signal(str, str)
    host = Signal(dict)
    command = Signal(list)
    eta = Signal(float, float)

    def on_phase(self, p): self.phase.emit(p)
    def on_progress(self, d, t): self.progress.emit(d, t)
    def on_log(self, lvl, msg): self.log.emit(lvl, msg)
    def on_host_update(self, d): self.host.emit(d)
    def on_command(self, argv): self.command.emit(list(argv))
    def on_eta(self, pct, rem): self.eta.emit(pct, rem)


class ScanWorker(QThread):
    finished_ok = Signal(object)   # ScanResult
    failed = Signal(str)
    # re-exposed for the window
    phase = Signal(str)
    progress = Signal(int, int)
    log = Signal(str, str)
    eta = Signal(float, float)
    command = Signal(list)

    def __init__(self, spec, cfg, translator, profile_id="", parent=None):
        super().__init__(parent)
        self._spec = spec
        self._cfg = cfg
        self._tr = translator
        self._profile = profile_id
        self._token = CancelToken()
        self._sink = _SignalSink()
        self._sink.phase.connect(self.phase)
        self._sink.progress.connect(self.progress)
        self._sink.log.connect(self.log)
        self._sink.eta.connect(self.eta)
        self._sink.command.connect(self.command)

    def cancel(self):
        self._token.cancel()

    def run(self):
        try:
            result = orchestrator.run(
                self._spec, self._cfg, token=self._token,
                sink=self._sink, i18n=self._tr, profile_id=self._profile)
            self.finished_ok.emit(result)
        except Exception as e:  # never crash the UI
            self.failed.emit(repr(e))
