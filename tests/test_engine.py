"""Engine tests (Qt-free). Run with: pytest -q"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abilithic_scan.core import normalize
from abilithic_scan.core.models import ScanResult, Exposure
from abilithic_scan.engine.command_builder import ScanSpec, build, preview
from abilithic_scan.engine import xml_parser, analyzer

SAMPLE_XML = """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap -sV 10.0.0.5" start="1" version="7.95">
  <host>
    <status state="up" reason="arp-response"/>
    <address addr="10.0.0.5" addrtype="ipv4"/>
    <hostnames><hostname name="dc01.lab" type="PTR"/></hostnames>
    <ports>
      <port protocol="tcp" portid="3389">
        <state state="open" reason="syn-ack"/>
        <service name="ms-wbt-server" product="Microsoft Terminal Services" method="probed" conf="10"/>
      </port>
      <port protocol="tcp" portid="445">
        <state state="open" reason="syn-ack"/>
        <service name="microsoft-ds" method="probed" conf="10"/>
        <script id="smb-vuln-ms17-010" output="State: VULNERABLE to MS17-010 (EternalBlue)"/>
      </port>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="8.9" method="probed" conf="10"/>
      </port>
    </ports>
    <os><osmatch name="Microsoft Windows Server 2019" accuracy="96"/></os>
  </host>
  <runstats><finished elapsed="3.2" summary="done"/></runstats>
</nmaprun>"""


def test_normalize_targets():
    assert normalize.is_ipv4("192.168.1.1")
    assert normalize.is_cidr("10.0.0.0/24")
    assert normalize.is_hostname("example.com")
    assert normalize.is_ipv6("::1")
    assert normalize.is_range("10.0.0.1-50")
    assert normalize.is_private("10.0.0.5")
    assert not normalize.is_private("8.8.8.8")
    valid, invalid = normalize.validate_targets("example.com 10.0.0.0/24 not a host!!")
    assert "example.com" in valid and invalid


def test_command_builder_preset():
    spec = ScanSpec(targets=["10.0.0.5"], preset_args=["-T4", "-A", "-v"])
    args = build(spec)
    assert args[:3] == ["-T4", "-A", "-v"]
    assert args[-1] == "10.0.0.5"
    assert "nmap " in preview(spec)


def test_command_builder_builder_mode_and_nse():
    spec = ScanSpec(targets=["10.0.0.5"], scan_type="-sS", service_detect=True,
                    ports="-p 80,443", nse=["vuln"], nse_args="mincvss=7.0")
    args = build(spec)
    assert "-sS" in args and "-sV" in args
    assert "--script" in args and "vuln" in args
    assert "--script-args" in args and "mincvss=7.0" in args


def test_connect_fallback():
    spec = ScanSpec(targets=["10.0.0.5"], scan_type="-sS", use_connect_fallback=True)
    args = build(spec)
    assert "-sT" in args and "-sS" not in args


def test_xml_parse():
    hosts, version, meta = xml_parser.parse_string(SAMPLE_XML)
    assert version == "7.95"
    assert len(hosts) == 1
    h = hosts[0]
    assert h.address == "10.0.0.5"
    assert h.primary_name() == "dc01.lab"
    assert len(h.open_ports()) == 3
    assert h.os_matches[0].accuracy == 96


def test_criticality_and_priorities():
    hosts, _, _ = xml_parser.parse_string(SAMPLE_XML)
    for h in hosts:
        h.exposure = Exposure.INTERNAL.value
    priorities = analyzer.analyze(hosts, i18n=lambda k: k)
    sev = {p.port: p.severity for p in priorities}
    # SMB with EternalBlue evidence must be HIGH or CRITICAL
    assert sev.get(445) in ("HIGH", "CRITICAL")
    # RDP base is HIGH
    assert sev.get(3389) in ("HIGH", "CRITICAL")
    # host risk grade rolls up to the worst
    assert hosts[0].risk_grade in ("HIGH", "CRITICAL")


def test_progress_line():
    out = xml_parser.parse_progress_line(
        "SYN Stealth Scan Timing: About 42.10% done; ETC: 12:00 (0:00:30 remaining)")
    assert out is not None
    pct, remaining = out
    assert round(pct) == 42 and remaining == 30


def test_summary_roundtrip():
    hosts, _, _ = xml_parser.parse_string(SAMPLE_XML)
    analyzer.analyze(hosts, i18n=lambda k: k)
    res = ScanResult()
    res.hosts = hosts
    res.summary = analyzer.summarize(hosts)
    d = res.to_dict()
    res2 = ScanResult.from_dict(d)
    assert len(res2.hosts) == 1
    assert res2.hosts[0].open_ports()[0].criticality.severity
