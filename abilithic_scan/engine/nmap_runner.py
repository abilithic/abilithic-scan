"""Run nmap as a subprocess: human-readable output to stdout (for the live log
and progress), XML to a temp file (for reliable parsing). Cancellable.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

from ..core.cancel import CancelToken, CancelledError
from ..core.events import NullSink
from . import xml_parser

_CREATE_NO_WINDOW = 0x08000000 if sys.platform.startswith("win") else 0


def run(nmap_path: str, args: list, token: CancelToken | None = None,
        sink=None) -> tuple:
    """Execute nmap. Returns (hosts, nmap_version, meta). Raises CancelledError
    if cancelled. Never lets a non-zero exit crash the caller."""
    token = token or CancelToken()
    sink = sink or NullSink()

    fd, xml_path = tempfile.mkstemp(suffix=".xml", prefix="abilithic_")
    os.close(fd)

    argv = [nmap_path, "-oX", xml_path, "--stats-every", "2s", *args]
    sink.on_command(argv)
    sink.on_log("INFO", " ".join(argv))

    try:
        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, universal_newlines=True,
            creationflags=_CREATE_NO_WINDOW)
    except FileNotFoundError:
        sink.on_log("ERROR", "nmap not found")
        _cleanup(xml_path)
        return [], "", {"error": "nmap_not_found"}

    try:
        for line in iter(proc.stdout.readline, ""):
            if token.cancelled:
                _terminate(proc)
                raise CancelledError()
            line = line.rstrip("\n")
            if not line:
                continue
            prog = xml_parser.parse_progress_line(line)
            if prog:
                pct, remaining = prog
                sink.on_eta(pct, remaining)
                sink.on_progress(int(pct), 100)
            else:
                sink.on_log("INFO", line)
        proc.wait()
    finally:
        try:
            proc.stdout.close()
        except Exception:
            pass

    hosts, version, meta = xml_parser.parse_file(xml_path)
    _cleanup(xml_path)
    return hosts, version, meta


def _terminate(proc):
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def _cleanup(path):
    try:
        os.remove(path)
    except Exception:
        pass
