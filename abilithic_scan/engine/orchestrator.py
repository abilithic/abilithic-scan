"""Scan orchestrator. Pure engine — never imports Qt.

Builds the command, runs nmap, parses results, classifies exposure, scores
criticality, and returns a complete (or partial-on-cancel) ScanResult.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from .. import __version__
from ..core.cancel import CancelToken, CancelledError
from ..core.events import NullSink
from ..core.models import ScanResult, ScanMeta, Exposure
from ..core.normalize import is_private
from . import command_builder, nmap_runner, locator, analyzer


def run(spec, cfg, token: CancelToken | None = None, sink=None, i18n=None,
        profile_id: str = "") -> ScanResult:
    token = token or CancelToken()
    sink = sink or NullSink()
    i18n = i18n or (lambda k: k)

    result = ScanResult()
    meta: ScanMeta = result.scan_meta
    meta.app_version = __version__
    meta.profile = profile_id
    meta.locale = getattr(cfg, "language", "id")
    meta.started_at = datetime.now(timezone.utc).isoformat()
    meta.elevated = locator.is_elevated()
    t0 = time.time()

    nmap_path = locator.find_nmap()
    if not nmap_path:
        meta.error = "nmap_not_found"
        sink.on_log("ERROR", i18n("log.no_nmap"))
        meta.finished_at = datetime.now(timezone.utc).isoformat()
        return result

    meta.nmap_version = locator.nmap_version(nmap_path)

    # Decide SYN vs Connect fallback when not elevated.
    if not meta.elevated:
        spec.use_connect_fallback = True

    args = command_builder.build(spec)
    meta.scan_args = args
    meta.command = command_builder.preview(spec)

    try:
        sink.on_phase("scan")
        hosts, version, run_meta = nmap_runner.run(nmap_path, args, token, sink)
        if version:
            meta.nmap_version = f"Nmap {version}"
        if run_meta.get("error"):
            meta.error = run_meta["error"]

        # classify exposure (public vs internal) from the target addresses
        for h in hosts:
            h.exposure = (Exposure.INTERNAL.value if is_private(h.address)
                          else Exposure.PUBLIC.value if h.address
                          else Exposure.UNKNOWN.value)

        sink.on_phase("score")
        result.priorities = analyzer.analyze(
            hosts, i18n, getattr(cfg, "crit_weights", {}))
        result.hosts = hosts
        result.summary = analyzer.summarize(hosts)
        for h in hosts:
            sink.on_host_update({"address": h.address, "grade": h.risk_grade})

    except CancelledError:
        meta.was_cancelled = True
        sink.on_log("WARN", i18n("log.cancelled"))
    except Exception as e:  # never crash the UI thread
        meta.error = repr(e)
        sink.on_log("ERROR", repr(e))
    finally:
        meta.finished_at = datetime.now(timezone.utc).isoformat()
        meta.duration_s = round(time.time() - t0, 2)

    return result
