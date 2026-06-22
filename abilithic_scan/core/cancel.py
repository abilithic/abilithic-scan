"""Cooperative cancellation token shared between the GUI and the engine."""
from __future__ import annotations

import threading


class CancelledError(Exception):
    """Raised when a scan is cancelled by the user."""


class CancelToken:
    def __init__(self) -> None:
        self._ev = threading.Event()

    def cancel(self) -> None:
        self._ev.set()

    @property
    def cancelled(self) -> bool:
        return self._ev.is_set()

    def check(self) -> None:
        if self._ev.is_set():
            raise CancelledError()
