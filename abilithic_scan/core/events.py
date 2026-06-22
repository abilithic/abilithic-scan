"""Engine -> UI event sink. The engine never imports Qt; it only calls these hooks.

The GUI worker provides an implementation that re-emits each call as a Qt signal
(marshalling to the UI thread). A headless CLI provides a printing implementation.
"""
from __future__ import annotations

from typing import Protocol


class EventSink(Protocol):
    def on_phase(self, phase: str) -> None: ...
    def on_progress(self, done: int, total: int) -> None: ...
    def on_log(self, level: str, message: str) -> None: ...
    def on_host_update(self, host_dict: dict) -> None: ...
    def on_command(self, argv: list) -> None: ...
    def on_eta(self, percent: float, eta_seconds: float) -> None: ...


class NullSink:
    def on_phase(self, phase: str) -> None: pass
    def on_progress(self, done: int, total: int) -> None: pass
    def on_log(self, level: str, message: str) -> None: pass
    def on_host_update(self, host_dict: dict) -> None: pass
    def on_command(self, argv: list) -> None: pass
    def on_eta(self, percent: float, eta_seconds: float) -> None: pass


class PrintSink:
    def on_phase(self, phase: str) -> None: print(f"[phase] {phase}")
    def on_progress(self, done: int, total: int) -> None: print(f"[progress] {done}/{total}")
    def on_log(self, level: str, message: str) -> None: print(f"[{level}] {message}")
    def on_host_update(self, host_dict: dict) -> None: print(f"[host] {host_dict.get('address')}")
    def on_command(self, argv: list) -> None: print("[cmd] " + " ".join(argv))
    def on_eta(self, percent: float, eta_seconds: float) -> None:
        print(f"[eta] {percent:.1f}% ~{int(eta_seconds)}s")
