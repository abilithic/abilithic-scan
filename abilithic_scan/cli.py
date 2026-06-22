"""Optional headless CLI. Example:
    python -m abilithic_scan.cli 192.168.1.0/24 --profile quick --lang en --excel out.xlsx
"""
from __future__ import annotations

import argparse

from .core.config import load_config
from .core.normalize import validate_targets
from .core.events import PrintSink
from .engine import presets
from .engine.command_builder import ScanSpec
from .engine.orchestrator import run
from .i18n import Translator
from . import reports


def main(argv=None):
    ap = argparse.ArgumentParser(prog="abilithic-scan")
    ap.add_argument("targets", nargs="+", help="IP / host / CIDR / range")
    ap.add_argument("--profile", default="quick")
    ap.add_argument("--lang", default="id", choices=["id", "en"])
    ap.add_argument("--script", default="", help="comma-separated NSE expressions")
    ap.add_argument("--excel", default="", help="write a formatted .xlsx report")
    ap.add_argument("--html", default="")
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)

    cfg = load_config()
    cfg.language = args.lang
    tr = Translator(args.lang)

    valid, invalid = validate_targets(" ".join(args.targets))
    if invalid:
        print("Invalid targets:", ", ".join(invalid))
    prof = presets.profile_by_id(args.profile) or {}
    spec = ScanSpec(targets=valid, preset_args=list(prof.get("args", [])),
                    nse=[x for x in args.script.split(",") if x])

    result = run(spec, cfg, sink=PrintSink(), i18n=tr, profile_id=args.profile)

    s = result.summary or {}
    print(f"\n{s.get('hosts_up', 0)} hosts up, {s.get('open_ports', 0)} open ports.")
    for p in result.priorities:
        print(f"  [{p.severity}] {p.host} {p.title} — {p.advice}")

    if args.excel:
        reports.save_xlsx(result, args.excel, tr); print("Excel:", args.excel)
    if args.html:
        reports.save_html(result, args.html, tr); print("HTML:", args.html)
    if args.json:
        reports.save_json(result, args.json); print("JSON:", args.json)


if __name__ == "__main__":
    main()
