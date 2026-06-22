"""Validate & normalize scan targets: IPv4/IPv6, CIDR, ranges, hostnames, files."""
from __future__ import annotations

import ipaddress
import re

_HOSTNAME = re.compile(
    r"^(?=.{1,253}$)([a-zA-Z0-9_](?:[a-zA-Z0-9_-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,63}$"
)
# nmap-style ranges like 192.168.1.1-50 or 10.0.0-2.1-254
_OCTET_RANGE = re.compile(r"^(\d{1,3}|\d{1,3}-\d{1,3}|\*)(\.(\d{1,3}|\d{1,3}-\d{1,3}|\*)){3}$")


def is_ipv4(t: str) -> bool:
    try:
        ipaddress.IPv4Address(t)
        return True
    except ValueError:
        return False


def is_ipv6(t: str) -> bool:
    try:
        ipaddress.IPv6Address(t)
        return True
    except ValueError:
        return False


def is_cidr(t: str) -> bool:
    try:
        ipaddress.ip_network(t, strict=False)
        return "/" in t
    except ValueError:
        return False


def is_hostname(t: str) -> bool:
    return bool(_HOSTNAME.match(t))


def is_range(t: str) -> bool:
    return bool(_OCTET_RANGE.match(t)) and ("-" in t or "*" in t)


def is_valid_target(t: str) -> bool:
    t = t.strip()
    if not t:
        return False
    return any((is_ipv4(t), is_ipv6(t), is_cidr(t), is_hostname(t), is_range(t)))


def is_private(t: str) -> bool:
    """Best-effort: is this target on a private/internal range?"""
    try:
        if is_cidr(t):
            return ipaddress.ip_network(t, strict=False).is_private
        if is_ipv4(t) or is_ipv6(t):
            return ipaddress.ip_address(t).is_private
    except ValueError:
        pass
    return False


def parse_targets(raw: str) -> list:
    """Split a free-text target box into a clean, de-duplicated list."""
    parts = re.split(r"[\s,;]+", raw.strip())
    out, seen = [], set()
    for p in parts:
        p = p.strip()
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def validate_targets(raw: str):
    """Return (valid_list, invalid_list)."""
    valid, invalid = [], []
    for t in parse_targets(raw):
        (valid if is_valid_target(t) else invalid).append(t)
    return valid, invalid
