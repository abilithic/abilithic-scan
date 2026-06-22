"""Parse Nmap XML output (-oX) into the canonical model objects.

Uses the stdlib ElementTree so the engine has no hard third-party parser
dependency. Tolerant of partial/odd output.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from ..core.models import (
    Host, Port, Service, ScriptResult, OSMatch, Severity)

_CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)


def parse_file(path: str) -> tuple:
    """Return (hosts, nmap_version, meta_dict). Never raises on bad input."""
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception:
        return [], "", {}
    return _parse_root(root)


def parse_string(xml: str) -> tuple:
    try:
        root = ET.fromstring(xml)
    except Exception:
        return [], "", {}
    return _parse_root(root)


def _parse_root(root) -> tuple:
    nmap_version = root.get("version", "")
    meta = {
        "args": root.get("args", ""),
        "start": root.get("startstr", ""),
    }
    runstats = root.find("runstats/finished")
    if runstats is not None:
        meta["elapsed"] = runstats.get("elapsed", "")
        meta["summary"] = runstats.get("summary", "")
    hosts = [_parse_host(h) for h in root.findall("host")]
    return hosts, nmap_version, meta


def _parse_host(h) -> Host:
    host = Host()
    status = h.find("status")
    if status is not None:
        host.state = status.get("state", "up")
        host.reason = status.get("reason", "")

    for addr in h.findall("address"):
        atype = addr.get("addrtype", "")
        if atype in ("ipv4", "ipv6"):
            host.address = addr.get("addr", "")
            host.addrtype = atype
        elif atype == "mac":
            host.mac = addr.get("addr", "")
            host.vendor = addr.get("vendor", "")

    names = h.find("hostnames")
    if names is not None:
        host.hostnames = [n.get("name", "") for n in names.findall("hostname") if n.get("name")]

    ports = h.find("ports")
    if ports is not None:
        for p in ports.findall("port"):
            host.ports.append(_parse_port(p))

    os_el = h.find("os")
    if os_el is not None:
        for m in os_el.findall("osmatch"):
            om = OSMatch(name=m.get("name", ""), accuracy=int(m.get("accuracy", "0") or 0))
            cls = m.find("osclass")
            if cls is not None:
                om.family = cls.get("osfamily", "")
                om.cpe = [c.text for c in cls.findall("cpe") if c.text]
            host.os_matches.append(om)

    up = h.find("uptime")
    if up is not None and up.get("seconds"):
        try:
            host.uptime_seconds = int(up.get("seconds"))
        except ValueError:
            pass

    dist = h.find("distance")
    if dist is not None and dist.get("value"):
        try:
            host.distance = int(dist.get("value"))
        except ValueError:
            pass

    trace = h.find("trace")
    if trace is not None:
        for hop in trace.findall("hop"):
            host.traceroute.append({
                "ttl": hop.get("ttl", ""), "ip": hop.get("ipaddr", ""),
                "rtt": hop.get("rtt", ""), "host": hop.get("host", ""),
            })

    # host-level scripts (hostscript)
    hs = h.find("hostscript")
    if hs is not None:
        extra = [_parse_script(s) for s in hs.findall("script")]
        if host.ports:
            host.ports[0].scripts.extend(extra)
    return host


def _parse_port(p) -> Port:
    port = Port()
    try:
        port.portid = int(p.get("portid", "0") or 0)
    except ValueError:
        port.portid = 0
    port.protocol = p.get("protocol", "tcp")
    st = p.find("state")
    if st is not None:
        port.state = st.get("state", "open")
        port.reason = st.get("reason", "")
    svc = p.find("service")
    if svc is not None:
        port.service = Service(
            name=svc.get("name", ""), product=svc.get("product", ""),
            version=svc.get("version", ""), extrainfo=svc.get("extrainfo", ""),
            ostype=svc.get("ostype", ""), tunnel=svc.get("tunnel", ""),
            method=svc.get("method", ""),
            conf=int(svc.get("conf", "0") or 0),
            cpe=[c.text for c in svc.findall("cpe") if c.text],
        )
    for s in p.findall("script"):
        port.scripts.append(_parse_script(s))
    return port


def _parse_script(s) -> ScriptResult:
    out = s.get("output", "") or ""
    cves = sorted(set(m.upper() for m in _CVE_RE.findall(out)))
    sev = Severity.INFO.value
    low = out.lower()
    if any(k in low for k in ("vulnerable", "state: vulnerable", "exploit")):
        sev = Severity.HIGH.value
    return ScriptResult(id=s.get("id", ""), output=out.strip(), severity=sev, cve=cves)


# --------------------------------------------------------------------------- #
# Live progress parsing from human-readable stdout (--stats-every)            #
# --------------------------------------------------------------------------- #
_PCT_RE = re.compile(r"About\s+([\d.]+)%\s+done")
_REMAIN_RE = re.compile(r"\(([\d:]+)\s+remaining\)")


def parse_progress_line(line: str):
    """Return (percent, remaining_seconds) or None for a stats line."""
    m = _PCT_RE.search(line)
    if not m:
        return None
    pct = float(m.group(1))
    remaining = 0.0
    r = _REMAIN_RE.search(line)
    if r:
        parts = [int(x) for x in r.group(1).split(":")]
        while len(parts) < 3:
            parts.insert(0, 0)
        remaining = parts[0] * 3600 + parts[1] * 60 + parts[2]
    return pct, remaining
