"""ScanSpec -> Nmap argument list. The single source of truth shared by the
GUI command preview and the actual runner: what the user sees is what runs.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScanSpec:
    targets: list = field(default_factory=list)
    exclude: list = field(default_factory=list)
    # Either use a preset's raw args ...
    preset_args: list = field(default_factory=list)
    # ... or compose from the technique builder:
    discovery: list = field(default_factory=list)   # e.g. ["-Pn"], ["-sn"], ["-PR"], ["-n"]
    scan_type: str = ""                              # e.g. "-sS", "-sT", "-sU"
    ipv6: bool = False
    ports: str = ""                                  # e.g. "-p-", "-p 22,80", "-F", "--top-ports 1000"
    open_only: bool = False                          # --open
    service_detect: bool = False                     # -sV
    version_intensity: int | None = None
    os_detect: bool = False                          # -O
    traceroute: bool = False
    aggressive: bool = False                         # -A
    timing: str = "-T4"
    min_rate: int | None = None
    nse: list = field(default_factory=list)          # list of --script expressions
    nse_args: str = ""
    evasion: list = field(default_factory=list)
    extra_flags: list = field(default_factory=list)  # raw custom flags (advanced)
    use_connect_fallback: bool = False               # force -sT when not elevated


def _split_flags(text: str) -> list:
    return [t for t in text.replace("\n", " ").split(" ") if t]


def build(spec: ScanSpec) -> list:
    """Return the nmap argument list (without the binary path or -oX output)."""
    args: list = []

    if spec.ipv6:
        args.append("-6")

    # Preset mode: take args verbatim, then append targets/exclude later.
    if spec.preset_args:
        args.extend(spec.preset_args)
    else:
        args.extend(spec.discovery)
        if spec.use_connect_fallback and spec.scan_type in ("-sS", ""):
            args.append("-sT")
        elif spec.scan_type:
            args.append(spec.scan_type)

        if spec.ports:
            args.extend(_split_flags(spec.ports))
        if spec.open_only:
            args.append("--open")

        if spec.aggressive:
            args.append("-A")
        else:
            if spec.service_detect:
                args.append("-sV")
                if spec.version_intensity is not None:
                    args += ["--version-intensity", str(spec.version_intensity)]
            if spec.os_detect:
                args.append("-O")
            if spec.traceroute:
                args.append("--traceroute")

        if spec.timing:
            args.append(spec.timing)
        if spec.min_rate:
            args += ["--min-rate", str(spec.min_rate)]

        args.extend(spec.evasion)

    # NSE applies in both preset and builder modes (skipped if a preset already
    # carries a --script of its own).
    if spec.nse and "--script" not in args:
        args += ["--script", ",".join(spec.nse)]
    if spec.nse_args:
        args += ["--script-args", spec.nse_args]

    args.extend(spec.extra_flags)

    for ex in spec.exclude:
        args += ["--exclude", ex]

    args.extend(spec.targets)
    return args


def preview(spec: ScanSpec, nmap_name: str = "nmap") -> str:
    """Human-readable command line for the GUI preview."""
    return nmap_name + " " + " ".join(build(spec))
