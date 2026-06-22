# Changelog

All notable changes to Abilithic Scan are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026
### Added
- First release: friendly GUI front-end for the full power of Nmap.
- Ready-made scan profiles (Quick, Quick+Version, Intense, Intense All Ports,
  Intense UDP, Ping Sweep, Discovery, Vuln, Stealth) plus custom flags.
- Full **NSE script picker**: 14 categories, curated bundles, custom expressions
  and script-args, with beginner hints and safety badges.
- **Port Criticality Engine** — transparent, context-aware severity per open
  port (e.g. RDP/SMB/Redis), with human-readable reasons and recommendations.
- **Priorities** view: "what to look at first", sorted by criticality.
- Live command preview (what you see is what runs) and **Learning Mode**.
- Live log, real progress + ETA, cancellable scans.
- **Polished Excel (.xlsx) report** with Summary, Priorities, Hosts, Open Ports,
  Services, NSE/CVE and Appendix sheets — plus HTML, JSON and CSV exports.
- Bilingual UI & reports (Bahasa Indonesia / English).
- Dark/light theme, Abilithic branding.
- TCP Connect fallback when not elevated; Npcap detection guidance.
- Single-file Windows `.exe` build (PyInstaller) + GitHub Actions release build.
