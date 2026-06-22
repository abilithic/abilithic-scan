# Third-Party Licenses

Abilithic Scan is a graphical front-end. It does not reimplement Nmap; it runs
the official Nmap engine and parses its output. The components below ship with
or are used by the application and remain under their own licenses.

## Nmap — Nmap Public Source License (NPSL)

Nmap is © Nmap Software LLC and is distributed under the **Nmap Public Source
License (NPSL)**, which is based on GPLv2 with additional terms. Key points
relevant to this project:

- Redistribution is permitted for open-source works that comply with the
  GPL/NPSL terms.
- The NPSL **prohibits embedding Nmap inside proprietary/commercial products**
  without a separate commercial (OEM) license from the Nmap Project.
- Applications that merely **execute a copy of Nmap provided by the end user**,
  or that **parse user-provided Nmap output**, are not bound by the NPSL.

License text: https://nmap.org/npsl/ · Legal notes: https://nmap.org/book/man-legal.html

**What this means for Abilithic Scan:** the app is open-source (MIT). If you
publish a build that *bundles* `nmap.exe`, ensure your distribution complies
with the NPSL (or obtain an Nmap OEM license). Alternatively, ship without the
Nmap binary and let the app use an Nmap that the user installs.

## Npcap

Npcap (the Windows packet-capture driver required for SYN/UDP/OS scans) has its
own license and **may not be redistributed without permission** from the Nmap
Project (contact sales@nmap.com). For this reason Abilithic Scan does **not**
redistribute Npcap. On first run it detects whether Npcap is installed and, if
not, guides the user to install the official Npcap from https://npcap.com.
Without Npcap, the app still works using TCP Connect (`-sT`) scans.

## PySide6 (Qt for Python)

Licensed under the **LGPL v3**. https://www.qt.io/licensing/

## openpyxl

Licensed under the **MIT License**. https://openpyxl.readthedocs.io/

---

By using or redistributing Abilithic Scan you agree to comply with all of the
above licenses in addition to the project's own MIT license.
