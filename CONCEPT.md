<div align="center">

# 🛰️ Abilithic Scan

### Network Mapping, Made Obvious — *the full power of Nmap, without the command line.*

**Konsep Teknis Lengkap (Hulu → Hilir) · Full Technical Concept**
Versi dokumen: `0.2 — draft` · Penulis: Abil Khosim · 2026

</div>

---

> **TL;DR.** Abilithic Scan adalah pembungkus GUI desktop untuk **Nmap** —
> seperti Zenmap, tetapi dirancang agar **pemula langsung paham**, mendukung
> **seluruh fungsi Nmap** (semua teknik scan **dan** semua skrip NSE) secara penuh,
> menilai **kritikalitas tiap port terbuka secara otomatis & akurat** (mis. RDP
> terbuka → HIGH/CRITICAL), dan mengekspor hasil langsung ke **file Excel (.xlsx)
> rapi & berformat** (bukan CSV mentah). Satu file `.exe`, tinggal klik dan jalan.
> UI dua bahasa (Indonesia / English) dengan **hint penjelasan di setiap menu &
> skrip**. Lebih **cepat** (scan dua-fase + timing pintar) tapi tetap **akurat**.
> Arsitektur mengikuti pola **Abilithic Recon** sehingga kedua tool satu keluarga.

**Perubahan di v0.2 dokumen ini:** (1) **Mesin Kritikalitas Port** transparan &
sadar-konteks — §8; (2) cakupan **NSE penuh** dengan script browser, argumen, CVE,
& skrip kustom — §7; (3) **strategi Performa & Akurasi** (scan dua-fase) — §13;
(4) **Tinjauan Konsep**: celah yang ditemukan & ditambal (IPv6, exclude, resume,
input/output, dll) — §20.

---

## 📑 Daftar Isi

1. [Posisi Produk & Filosofi](#1-posisi-produk--filosofi)
2. [Masalah yang Diselesaikan](#2-masalah-yang-diselesaikan)
3. [Gambaran Konsep](#3-gambaran-konsep)
4. [Arsitektur Hulu → Hilir](#4-arsitektur-hulu--hilir)
5. [Mesin Nmap: Integrasi, Bundling & Lisensi](#5-mesin-nmap-integrasi-bundling--lisensi)
6. [Katalog Teknik Scan (Nmap Penuh) + Hint Pemula](#6-katalog-teknik-scan-nmap-penuh--hint-pemula)
7. [NSE — Nmap Scripting Engine (Penuh)](#7-nse--nmap-scripting-engine-penuh)
8. [★ Mesin Kritikalitas Port (Otomatis & Akurat)](#8--mesin-kritikalitas-port-otomatis--akurat)
9. [Profil Siap-Pakai (Presets)](#9-profil-siap-pakai-presets)
10. [Desain GUI & Menu (dengan Hint Tiap Item)](#10-desain-gui--menu-dengan-hint-tiap-item)
11. [Model Data (Kontrak Versioned)](#11-model-data-kontrak-versioned)
12. [Laporan Excel yang Rapi (Fitur Unggulan)](#12-laporan-excel-yang-rapi-fitur-unggulan)
13. [Performa & Akurasi (Lebih Cepat, Tetap Akurat)](#13-performa--akurasi-lebih-cepat-tetap-akurat)
14. [Internasionalisasi (ID / EN)](#14-internasionalisasi-id--en)
15. [Build, Packaging & Single .exe](#15-build-packaging--single-exe)
16. [Struktur Folder Proyek](#16-struktur-folder-proyek)
17. [Keamanan, Etika & Consent](#17-keamanan-etika--consent)
18. [Roadmap](#18-roadmap)
19. [Ide Tambahan / Pembeda (Value-Add)](#19-ide-tambahan--pembeda-value-add)
20. [Tinjauan Konsep: Celah yang Ditambal & Peningkatan](#20-tinjauan-konsep-celah-yang-ditambal--peningkatan)
21. [Lampiran: Pemetaan Flag Nmap](#21-lampiran-pemetaan-flag-nmap)

---

## 1. Posisi Produk & Filosofi

| | |
|---|---|
| **Nama** | Abilithic Scan |
| **Tagline** | *Network Mapping, Made Obvious.* |
| **Kategori** | Network discovery & port/service scanning (GUI front-end untuk Nmap) |
| **Pengguna** | Pemula keamanan, sysadmin, mahasiswa, blue-team internal, IT support |
| **Platform rilis** | Windows 10/11 64-bit (single `.exe`); jalan dari source di Linux/macOS |
| **Bahasa** | Indonesia & English (full UI + laporan) |
| **Lisensi app** | MIT untuk kode Abilithic; lihat §5 untuk komponen Nmap |
| **Saudara** | Abilithic Recon (attack-surface). Scan = *"apa yang terbuka di host yang sudah saya tahu"*; Recon = *"host apa saja yang dimiliki organisasi ini"* |

**Filosofi desain (4 pilar):**

1. **Obvious by default.** Setiap tombol, menu, opsi, dan skrip punya hint satu
   kalimat. Pemula tak perlu tahu arti `-sS` untuk memakainya — tapi tetap *bisa*
   belajar, karena setiap pilihan menampilkan flag Nmap yang dihasilkannya.
2. **No power lost.** **Seluruh fungsi Nmap** ada di sini — semua teknik scan
   (§6) **dan** seluruh 600+ skrip NSE (§7). Selalu ada **"Custom flags"** dan
   **command preview** real-time untuk pengguna mahir.
3. **Meaning, not just data.** Nmap memberi fakta ("port 3389 open"); Abilithic
   memberi **arti**: kritikalitas otomatis per port (§8) agar pemula langsung tahu
   *mana yang harus diperhatikan lebih dulu*.
4. **Fast but accurate.** Scan dua-fase + timing pintar mempercepat tanpa
   mengorbankan akurasi (§13).

---

## 2. Masalah yang Diselesaikan

Nmap adalah standar emas pemetaan jaringan, tetapi:

- **Curam untuk pemula.** Ratusan flag, mudah salah ketik, sulit diingat.
- **Zenmap menua & terbatas.** Tidak lagi dikembangkan aktif, tampilan kuno,
  bahasa lokal minim, ekspor berupa XML/teks — bukan laporan rapi untuk non-teknis.
- **Output mentah sulit dimaknai.** Pemula melihat "445/tcp open microsoft-ds"
  tapi **tidak tahu itu berbahaya**. Tak ada penilaian risiko bawaan.
- **Output tak presentable.** Stakeholder ingin tabel rapi & prioritas, bukan dump.
- **Setup ribet.** Harus install Nmap + Npcap, atur PATH, paham terminal.

**Abilithic Scan** menutup celah ini: kekuatan penuh Nmap, antarmuka yang mengajari
sambil dipakai, **penilaian kritikalitas otomatis**, dan output Excel yang langsung
presentable — dalam satu `.exe` yang tinggal dijalankan.

---

## 3. Gambaran Konsep

```
            ┌──────────────────────────────────────────────────────────────┐
            │                      ABILITHIC SCAN (.exe)                     │
            │                                                                │
   Target → │  GUI (PySide6) → Command Builder → Nmap Engine Runner          │ → XML stream
            │       ▲                 │                  │                    │
            │       │           (command preview)  (bundled nmap.exe + NSE)   │
            │       │                                    │                    │
            │  Live table ← Criticality Engine ← XML Parser ← Event Sink ←────┘
            │       │              (§8)                                       │
            │       └──→  Analysis & Priorities  →  Excel / HTML / JSON / CSV │
            └──────────────────────────────────────────────────────────────┘
```

Alur singkat pengguna:

1. Buka `.exe` → jendela utama muncul (tanpa console hitam).
2. Ketik/impor target (IP, hostname, CIDR `192.168.1.0/24`, range, atau file `.txt`).
3. Pilih **Profil** atau susun teknik & skrip sendiri. Lihat **command preview**.
4. Klik **Start**. Lihat progress, log live, dan tabel host/port terisi real-time —
   **berwarna sesuai kritikalitas**.
5. Klik baris untuk **detail** (port, service, versi, output NSE, OS, traceroute,
   *alasan* kritikalitas).
6. **Export ke Excel** (multi-sheet, ada sheet **Prioritas**) / HTML / JSON / CSV.

---

## 4. Arsitektur Hulu → Hilir

Mengikuti pola **Abilithic Recon**: **engine murni tanpa Qt**, GUI tipis, event sink,
token pembatalan, model data berversi, teknik/skrip/kritikalitas yang *pluggable* via
JSON, dan laporan yang membaca satu kontrak data yang sama.

```
abilithic_scan/
├── core/        # kontrak & util murni (tanpa Qt, tanpa Nmap)
│   ├── models.py        # dataclass berversi: ScanResult, Host, Port, Service, Criticality…
│   ├── events.py        # EventSink Protocol (engine → UI), NullSink, PrintSink
│   ├── cancel.py        # CancelToken + CancelledError
│   ├── config.py        # AppConfig berversi + migrasi (bobot kritikalitas dll)
│   ├── paths.py         # resource_path() (PyInstaller-aware), config_path()
│   └── normalize.py     # validasi & normalisasi target (IP/CIDR/range/host/IPv6)
│
├── engine/      # logika scan murni (tanpa Qt)
│   ├── nmap_runner.py   # spawn nmap.exe, streaming stdout, kelola proses & cancel
│   ├── command_builder.py # ScanSpec → argumen Nmap (single source of truth)
│   ├── xml_parser.py    # parse Nmap XML (-oX -) streaming → models incremental
│   ├── presets.py       # profil siap-pakai
│   ├── techniques.py    # katalog teknik (flag, butuh-root, bahaya, hint-key)
│   ├── nse.py           # katalog & indeks skrip NSE, kategori, argumen
│   ├── criticality.py   # ★ mesin kritikalitas port (§8)
│   ├── analyzer.py      # rangkum temuan, prioritas, roll-up risiko per host
│   ├── orchestrator.py  # rangkai semuanya → ScanResult
│   └── locator.py       # temukan binary nmap (bundled → PATH → auto-setup)
│
├── gui/         # PySide6 (satu-satunya yang impor Qt)
│   ├── app.py           # MainWindow, menu bar, status bar (hint), tema, bahasa
│   ├── target_panel.py  # input/impor target + validasi + riwayat
│   ├── profile_panel.py # pilih preset / builder teknik visual
│   ├── nse_browser.py   # ★ pencarian & pemilihan skrip NSE berkategori
│   ├── command_bar.py   # command preview + Start/Cancel/Pause
│   ├── results_table.py # QAbstractTableModel: host & port, sortable/filter, berwarna
│   ├── detail_pane.py   # detail per host (port, service, NSE, OS, traceroute, alasan)
│   ├── priorities_pane.py # ★ daftar "apa yang harus diperhatikan dulu"
│   ├── log_view.py      # log live + progress + ETA
│   ├── worker.py        # QThread; jalankan orchestrator, marshalling sinyal
│   ├── hints.py         # peta widget → kunci-hint
│   └── theme.py         # tema gelap/terang + palet severity
│
├── reports/     # membaca ScanResult → file (tanpa Qt)
│   ├── xlsx_report.py   # ★ Excel berformat rapi + sheet Prioritas (openpyxl)
│   ├── html_report.py   # laporan HTML mandiri
│   ├── json_report.py   # simpan/buka ulang scan
│   └── csv_report.py    # CSV (UTF-8 BOM) fallback
│
├── i18n/ (__init__.py, locales/{id,en}.json)
├── data/
│   ├── nmap/            # binary nmap + data + folder scripts NSE [bundled]
│   ├── npcap/           # (lihat §5 soal lisensi — di-fetch saat first-run)
│   ├── catalog/         # techniques.json, presets.json, nse-index.json
│   └── knowledge/       # port_criticality.json, kev.json (CISA KEV offline)
│
├── cli.py / __main__.py / main.py
└── tests/
```

**Aturan ketat (diwarisi dari Recon):** `engine/` & `core/` tak pernah impor Qt;
komunikasi engine→UI hanya lewat **`EventSink`**; **`CancelToken`** dicek tiap fase
& mematikan proses Nmap dengan rapi (hasil parsial tetap kembali); semua konsumen
membaca **`ScanResult`** yang sama; `command_builder.py` satu-satunya jembatan
`ScanSpec` → argumen Nmap (preview = perintah nyata).

**EventSink untuk Scan:**

```python
class EventSink(Protocol):
    def on_phase(self, phase: str) -> None: ...      # discover|port|service|nse|os|score
    def on_progress(self, done: int, total: int) -> None: ...
    def on_log(self, level: str, message: str) -> None: ...
    def on_host_update(self, host_dict: dict) -> None: ...   # host/port baru → tabel live
    def on_command(self, argv: list[str]) -> None: ...       # perintah final (Learning Mode)
    def on_eta(self, percent: float, eta_seconds: float) -> None: ...  # dari <taskprogress>
```

---

## 5. Mesin Nmap: Integrasi, Bundling & Lisensi

### 5.1 Cara kerja runner
Abilithic Scan **tidak menulis ulang Nmap**. Ia menjalankan `nmap.exe` sebagai
subprocess dengan output **XML streaming** (`-oX -`) lalu mem-parse-nya secara
streaming.

```python
argv = [nmap_path, "-oX", "-", "--stats-every", "1s", *spec_args, *targets]
proc = subprocess.Popen(argv, stdout=PIPE, stderr=PIPE, text=True,
                        creationflags=CREATE_NO_WINDOW)   # tak ada jendela hitam
for chunk in proc.stdout:
    parser.feed(chunk)           # → on_host_update / on_progress / on_eta
    if token.cancelled:
        proc.terminate()
```

Keunggulan vs. library Python: dukungan **penuh** semua flag & skrip Nmap; DB
OS/versi/NSE selalu sesuai versi Nmap yang dibundel.

### 5.2 Menemukan binary (`locator.py`)
1. **Bundled** `data/nmap/nmap.exe` (jalur utama) → 2. **PATH sistem** (jika user
punya versi sendiri) → 3. **Auto-setup** (tawarkan unduh installer resmi).

### 5.3 Npcap (driver capture) — wajib untuk SYN/raw/UDP/OS scan
Teknik andalan (`-sS`, `-sU`, `-O`) butuh **Npcap** terpasang sebagai driver. Saat
pertama jalan, app **mendeteksi Npcap**; bila belum ada, jalankan **installer Npcap**
sekali. Bila ditolak, app tetap bisa **TCP Connect (`-sT`)** tanpa Npcap/admin.

### 5.4 ⚖️ Catatan lisensi (wajib dipatuhi)
Kamu memilih **bundle Nmap** demi "tinggal run". Dua aturan tak bisa diabaikan:

- **Nmap** berlisensi **NPSL** (berbasis GPLv2). Distribusi **boleh** untuk karya
  open-source patuh GPL/NPSL, **dilarang** masuk produk **proprietary/komersial**.
  Karena Abilithic Scan direncanakan **open-source gratis**, agar aman pertimbangkan
  rilis biner ini **NPSL/GPL-kompatibel**, atau pakai model "menjalankan Nmap yang
  disediakan end-user" yang **tidak terikat** NPSL.
- **Npcap tidak boleh diredistribusi tanpa izin khusus** (`sales@nmap.com`).

**Rekomendasi patuh (tetap "tinggal run"):** bundle binary Nmap + **first-run
auto-setup Npcap** (mengunduh installer resmi ≠ redistribusi). Untuk offline,
sediakan "pilih installer Npcap manual". Untuk benar-benar satu file tanpa internet,
ajukan **izin OEM/Npcap**. Sertakan **`THIRD-PARTY-LICENSES.md`** & **Help ▸ Licenses**.

---

## 6. Katalog Teknik Scan (Nmap Penuh) + Hint Pemula

Semua teknik diekspos dengan **badge** (butuh admin? berisik? agresif?) & **hint dua
bahasa**. Tabel = isi `data/catalog/techniques.json`.

### 6.1 Host Discovery

| Opsi GUI | Flag | Hint (ID) | Hint (EN) | Admin |
|---|---|---|---|---|
| Ping biasa | `-sn` | Cek host hidup tanpa scan port. | Up-check, no port scan. | – |
| Lewati discovery | `-Pn` | Anggap semua host hidup (target yang blok ping). | Treat all hosts online. | – |
| ICMP echo | `-PE` | Ping ICMP klasik. | Classic ICMP echo. | ✔ |
| TCP SYN/ACK ping | `-PS` / `-PA` | Ping via SYN/ACK ke port tertentu. | Liveness via TCP SYN/ACK. | ✔ |
| UDP ping | `-PU` | Ping via UDP. | Liveness via UDP. | ✔ |
| ARP ping | `-PR` | Tercepat & akurat di LAN. | Fastest/accurate on LAN. | ✔ |
| SCTP/IP-proto ping | `-PY` / `-PO` | Ping SCTP atau protokol IP. | SCTP / IP-protocol ping. | ✔ |
| No DNS | `-n` | Jangan resolve DNS (lebih cepat). | Skip DNS (faster). | – |

### 6.2 Teknik Port Scan (inti)

| Opsi GUI | Flag | Hint (ID) | Hint (EN) | Catatan |
|---|---|---|---|---|
| **SYN (stealth)** ★ | `-sS` | Scan cepat & sopan; tak menyelesaikan koneksi. | Fast half-open scan. | admin+Npcap |
| **TCP Connect** | `-sT` | Aman tanpa admin; koneksi penuh OS. | No admin needed. | fallback |
| **UDP** | `-sU` | Layanan UDP (DNS, SNMP); lambat. | UDP services; slow. | admin |
| FIN/Xmas/Null | `-sF`/`-sX`/`-sN` | Trik flag TCP untuk mengelabui filter. | TCP-flag tricks evade filters. | admin |
| ACK / Window | `-sA` / `-sW` | Petakan aturan firewall. | Map firewall rules. | admin |
| Maimon | `-sM` | Trik FIN/ACK (BSD lama). | FIN/ACK BSD trick. | admin |
| **Idle/Zombie** | `-sI` | Super-siluman lewat host pihak ketiga. | Ultra-stealth via zombie host. | mahir |
| SCTP INIT/COOKIE | `-sY` / `-sZ` | Scan port SCTP (telekomunikasi). | SCTP port scan. | admin |
| IP protocol | `-sO` | Protokol IP yang didukung host. | Supported IP protocols. | admin |
| FTP bounce | `-b` | Scan via server FTP perantara (legacy). | Scan via relay FTP. | mahir |

### 6.3 Deteksi Layanan, Versi & OS

| Opsi GUI | Flag | Hint (ID) | Hint (EN) |
|---|---|---|---|
| Deteksi versi | `-sV` | Cari nama & versi layanan tiap port. | Service name & version per port. |
| Intensitas versi | `--version-intensity 0-9` / `--version-light` / `--version-all` | Seberapa "ngotot" menebak versi. | Version probe aggressiveness. |
| Deteksi OS | `-O` / `--osscan-guess` | Tebak sistem operasi host. | Guess the host OS. |
| Traceroute | `--traceroute` | Petakan jalur jaringan ke host. | Map the network path. |
| **Aggressive** | `-A` | Versi+OS+skrip default+traceroute sekaligus. | All-in-one deep scan. |

### 6.4 Pemilihan Port

| Opsi GUI | Flag | Hint (ID) | Hint (EN) |
|---|---|---|---|
| Top N | `--top-ports N` | Port paling umum (cepat). | Most common ports. |
| Semua port | `-p-` | 65.535 port (lengkap, lambat). | All 65,535 ports. |
| Spesifik/Range | `-p 22,80,443` / `-p 1-1024` | Port/rentang pilihanmu. | Chosen ports/range. |
| Fast | `-F` | 100 port teratas. | Top 100 ports. |
| Hanya yang terbuka | `--open` | Sembunyikan port tertutup di hasil. | Show only open ports. |

### 6.5 Timing & Performa

| Opsi GUI | Flag | Hint (ID) | Hint (EN) |
|---|---|---|---|
| Template kecepatan | `-T0`…`-T5` | T0 pelan/siluman → T5 cepat/berisik. | T0 stealthy → T5 fast. |
| Laju paket | `--min-rate`/`--max-rate` | Batas paket per detik. | Packets-per-second floor/ceiling. |
| Paralelisme | `--min-hostgroup`/`--min-parallelism` | Berapa host/probe sekaligus. | Hosts/probes in parallel. |
| Retries & timeout | `--max-retries`/`--host-timeout` | Hindari membuang waktu. | Avoid wasting time. |
| Scan delay | `--scan-delay` | Jeda antar paket (hindari rate-limit). | Delay between packets. |

### 6.6 Firewall / IDS Evasion (mahir — badge ⚠)

| Opsi GUI | Flag | Hint (ID) | Hint (EN) |
|---|---|---|---|
| Fragmentasi | `-f` / `--mtu` | Pecah paket agar lolos filter. | Fragment packets. |
| Decoy / Spoof | `-D` / `-S` / `--spoof-mac` | Sembunyikan/palsukan identitas. | Hide/spoof identity. |
| Source port | `-g` | Pakai port sumber tertentu (mis. 53). | Fixed source port. |
| Data length / Bad checksum | `--data-length` / `--badsum` | Ubah paket untuk uji IDS. | Tweak packets for IDS tests. |
| Proxies / Interface | `--proxies` / `-e` | Lewatkan via proxy / pilih NIC. | Route via proxy / pick NIC. |

### 6.7 Input, Output & Misc (kelengkapan)

| Opsi GUI | Flag | Hint (ID) | Hint (EN) |
|---|---|---|---|
| IPv6 | `-6` | Scan target IPv6. | Scan IPv6 targets. |
| Impor target | `-iL <file>` | Muat daftar target dari file. | Load targets from file. |
| Target acak | `-iR <n>` | Pilih host acak di internet (riset). | Random internet hosts. |
| Exclude | `--exclude` / `--excludefile` | Kecualikan host tertentu. | Skip given hosts. |
| Resume | `--resume <file>` | Lanjutkan scan yang terputus. | Continue an interrupted scan. |
| Reason / Packet trace | `--reason` / `--packet-trace` | Tampilkan alasan & jejak paket. | Show reason/packet trace. |
| Simpan native | `-oA/-oN/-oG` | Simpan output asli Nmap (audit). | Save native Nmap output. |

---

## 7. NSE — Nmap Scripting Engine (Penuh)

NSE adalah "kekuatan super" Nmap: **600+ skrip resmi** dalam **14 kategori** untuk
penemuan mendalam, deteksi kerentanan, brute force, dan banyak lagi. Abilithic Scan
mengekspos **semuanya** lewat **Script Browser** yang ramah pemula.

### 7.1 14 kategori NSE (dengan hint & badge keamanan)

| Kategori | Hint (ID) | Hint (EN) | Badge |
|---|---|---|---|
| `default` | Skrip aman & berguna yang jalan dengan `-sC`. | Safe, useful scripts run by `-sC`. | ✅ aman |
| `safe` | Tidak mengganggu target. | Won't disrupt the target. | ✅ aman |
| `discovery` | Gali info jaringan/host lebih dalam. | Dig deeper into hosts/network. | ✅ aman |
| `version` | Bantu deteksi versi layanan. | Aid service/version detection. | ✅ aman |
| `auth` | Cek autentikasi/kredensial (mis. anon login). | Check auth/credentials. | ⚠ hati-hati |
| `broadcast` | Temukan host via siaran LAN. | Discover hosts via broadcast. | ✅ aman |
| `external` | Mengirim data ke layanan pihak ketiga. | Talks to 3rd-party services. | ⚠ privasi |
| `fuzzer` | Kirim input acak (uji ketahanan). | Send malformed input. | ⚠ intrusif |
| `intrusive` | Berisiko mengganggu target. | May disrupt the target. | ⚠ intrusif |
| `brute` | Tebak kredensial (login bruteforce). | Credential brute force. | ⚠ intrusif |
| `dos` | Uji denial-of-service (bisa merusak!). | Denial-of-service tests. | 🛑 berbahaya |
| `exploit` | Coba eksploitasi kerentanan aktif. | Actively exploit a vuln. | 🛑 berbahaya |
| `malware` | Deteksi backdoor/malware di host. | Detect backdoors/malware. | ✅ aman |
| `vuln` | **Deteksi kerentanan dikenal (Heartbleed, EternalBlue, dll).** | **Detect known vulns.** | ⚠ hati-hati |

> Skrip `vuln` hanya melapor bila kerentanan **benar-benar ditemukan** — ideal untuk
> pemula yang ingin tahu "apakah host ini rentan?".

### 7.2 Script Browser (GUI)

`gui/nse_browser.py` menyediakan:

- **Pencarian** real-time (nama, kategori, kata kunci) atas `data/catalog/nse-index.json`
  (indeks dibangun dari metadata `--script-help` tiap skrip).
- **Pengelompokan ganda**: per **kategori** *dan* per **target/tujuan** (HTTP, SMB,
  SSL/TLS, DNS, FTP, SMTP, Database, SNMP, RDP, SSH, IoT/ICS, …) — pemula memilih
  berdasarkan "apa yang ingin saya periksa".
- **Hint per skrip** (dua bahasa) dari deskripsi resmi skrip + contoh.
- **Checkbox** memilih banyak skrip; menghasilkan `--script <daftar/ekspresi>`.
- **Dukungan ekspresi penuh**: kategori (`--script vuln`), nama
  (`--script ssl-heartbleed`), wildcard (`--script "http-*"`), boolean
  (`--script "default and safe"`, `"not intrusive"`), file/direktori.

### 7.3 Editor argumen skrip
UI key-value → `--script-args` (mis. `http.useragent`, `userdb`, `passdb`,
`vulns.showall`, `mincvss=7.0`). Mendukung `--script-args-file`. Setiap argumen
umum diberi hint.

### 7.4 Deteksi CVE / kerentanan
- **`vulners.nse`** — cocokkan **CPE** hasil `-sV` ke basis data CVE; filter dengan
  `mincvss`; tampilkan skor CVSS + tautan. (butuh internet)
- **`vulscan.nse`** — alternatif **offline** (database lokal).
- Skrip `*-vuln-*` spesifik (mis. `smb-vuln-ms17-010`, `ssl-heartbleed`,
  `http-vuln-cve*`).
- **Output NSE dipetakan ke `Finding` + menaikkan kritikalitas port** (§8). CVE yang
  ada di **CISA KEV** (sedang dieksploitasi liar) otomatis dinaikkan ke **CRITICAL**.

### 7.5 Skrip kustom & pembaruan
- Pengguna bisa menaruh `.nse` di **folder skrip pengguna**; app menjalankan
  `--script-updatedb` agar terindeks.
- **Tools ▸ Update NSE** menyegarkan indeks & (opsional) `vulners`/`vulscan` DB.

### 7.6 Gerbang keamanan
Kategori `intrusive`, `brute`, `fuzzer` → dialog konfirmasi. `dos`, `exploit` →
konfirmasi **dua langkah** + badge 🛑 "dapat mengganggu/merusak target — lanjutkan
hanya jika Anda berwenang penuh." Default profil **tidak pernah** menyertakan ini.

### 7.7 Bundel skrip bernilai tinggi (contoh, dengan hint)

| Bundel GUI | Skrip / ekspresi | Hint (ID) |
|---|---|---|
| Cek kerentanan umum | `--script vuln` | Cari celah terkenal di semua layanan. |
| Enum SMB/Windows | `smb-os-discovery,smb-enum-shares,smb-vuln-ms17-010` | Info Windows, share, & EternalBlue. |
| Enum HTTP/Web | `http-title,http-headers,http-enum,http-methods` | Judul, header, folder, & metode web. |
| Audit SSL/TLS | `ssl-cert,ssl-enum-ciphers,ssl-heartbleed` | Sertifikat, cipher lemah, Heartbleed. |
| DNS | `dns-recursion,dns-zone-transfer` | Rekursi terbuka & zone transfer (AXFR). |
| Default credentials | `--script auth` | Cek login default/anonim. |
| Korelasi CVE | `vulners --script-args mincvss=7.0` | Daftar CVE berisiko tinggi per layanan. |

---

## 8. ★ Mesin Kritikalitas Port (Otomatis & Akurat)

**Tujuan:** pemula langsung tahu **mana yang harus diperhatikan dulu**. Setiap port
terbuka dinilai severity-nya secara **otomatis, akurat, dan transparan** (selalu ada
*alasan* yang bisa dibaca). Diimplementasikan di `engine/criticality.py` dengan basis
pengetahuan `data/knowledge/port_criticality.json` (editable, mirip `risk_weights`
di Recon).

### 8.1 Skala severity
`INFO → LOW → MEDIUM → HIGH → CRITICAL` (rank 0–4), warna konsisten di tabel, detail,
& Excel: CRITICAL=merah, HIGH=oranye, MEDIUM=kuning, LOW=biru, INFO=abu.

### 8.2 Cara penilaian (transparan, 5 faktor)
Severity final = fungsi yang dapat dijelaskan dari:

1. **Base service criticality** — dari knowledge base, di-key by **nama layanan**
   (hasil `-sV`) dengan fallback ke **nomor port**. Contoh: `ms-wbt-server`/3389 → HIGH.
2. **Konteks paparan** — **internet-facing** (IP publik) menaikkan; internal (RFC1918)
   menurunkan. "RDP internal" ≠ "RDP terbuka ke internet".
3. **Kelemahan protokol** — protokol **cleartext** (telnet, ftp, http, snmp v1/v2c,
   rlogin) menambah bobot.
4. **Autentikasi/state** — temuan NSE "anonymous/no-auth/default creds/world-readable"
   menaikkan (mis. Redis tanpa password → CRITICAL).
5. **Versi/EOL & CVE** — `-sV` + `vulners`/`*-vuln-*`; CVE → naik; **CVE di CISA KEV**
   (sedang dieksploitasi) → **CRITICAL** otomatis.

```
severity_final = clamp( max(base, evidence_floor) + context_modifiers )
```

Setiap port menyimpan **`CriticalityBreakdown`** (daftar `contributor`:
`factor, weight, reason`) → pemula melihat **"kenapa"** dalam bahasa biasa, bukan
sekadar label. Bobot ada di config sehingga bisa dikalibrasi tanpa rebuild.

### 8.3 Basis pengetahuan port (cuplikan representatif)

> `port_criticality.json` berisi ~200 entri. Berikut contoh yang mewakili logikanya.
> "Eskalasi" = kondisi yang menaikkan severity.

| Layanan / Port | Base | Eskalasi → | Alasan ringkas (yang ditampilkan ke pemula) |
|---|---|---|---|
| **RDP** 3389 | HIGH | **CRITICAL** bila internet-facing / BlueKeep | Remote Desktop; target favorit ransomware bila terbuka ke internet. |
| **SMB** 445 / 137-139 | HIGH | **CRITICAL** bila SMBv1/MS17-010/anon | Berbagi file Windows; sumber EternalBlue/WannaCry. |
| **Telnet** 23 | HIGH | — | Akses admin **tanpa enkripsi** — kredensial terlihat jelas. |
| **VNC** 5900-5906 | HIGH | **CRITICAL** bila tanpa password | Remote desktop; sering tanpa autentikasi. |
| **rlogin/rsh/rexec** 512-514 | HIGH | — | Layanan remote legacy tak aman. |
| **FTP** 21 | MEDIUM | **HIGH** bila anonymous login | Transfer file cleartext; cek anon. |
| **TFTP** 69/udp | HIGH | — | Tanpa autentikasi, sering bocor konfigurasi. |
| **NFS** 2049 | HIGH | **CRITICAL** bila world-readable | Berbagi file Unix; sering dapat dibaca siapa saja. |
| **MySQL** 3306 / **MSSQL** 1433 / **PostgreSQL** 5432 | HIGH | **CRITICAL** bila publik/no-pw | Database tak boleh terekspos ke internet. |
| **MongoDB** 27017 / **Redis** 6379 / **Elasticsearch** 9200 | HIGH | **CRITICAL** bila no-auth | Klasik kebocoran data & RCE bila tanpa auth. |
| **Memcached** 11211 | HIGH | — | Tanpa auth; risiko amplifikasi DDoS. |
| **Docker API** 2375 | **CRITICAL** | — | API tanpa autentikasi = ambil alih host penuh. |
| **Kubernetes** 6443 / kubelet 10250 | HIGH | **CRITICAL** bila anonymous | Bidang kendali klaster; sangat sensitif. |
| **SNMP** 161/udp | MEDIUM | **HIGH** bila community public/private | Info perangkat bocor via community string default. |
| **LDAP** 389 | MEDIUM | **HIGH** bila anonymous bind | Direktori; bind anonim membocorkan data. |
| **WinRM** 5985/5986 | MEDIUM | — | Remote management Windows. |
| **SSH** 22 | LOW | **MEDIUM** bila versi tua/algoritma lemah | Aman bila terkonfigurasi; target brute. |
| **HTTP** 80 | INFO | tergantung temuan web | Bergantung aplikasi di belakangnya. |
| **HTTPS** 443 | INFO | **MEDIUM** bila TLS lemah/expired | Periksa sertifikat & cipher. |
| **HTTP-alt** 8080/8000/8443 | LOW | **MEDIUM** | Sering panel admin/aplikasi internal. |
| **SMTP** 25 | LOW | **MEDIUM** bila open relay | Relay terbuka disalahgunakan untuk spam. |
| **DNS** 53 | LOW | **MEDIUM** bila rekursi/AXFR terbuka | Bisa untuk amplifikasi / bocor zona. |
| **NTP** 123/udp | LOW | **MEDIUM** bila monlist aktif | Risiko amplifikasi DDoS. |
| **IPMI/BMC** 623/udp | HIGH | — | Manajemen perangkat keras; sering rentan. |
| **X11** 6000-6009 | HIGH | — | Sering tanpa auth; bisa rekam layar/keystroke. |
| **Printer** 9100 | MEDIUM | — | Raw print; bisa disalahgunakan. |
| **Modbus** 502 / **S7** 102 / **BACnet** 47808 / **DNP3** 20000 | HIGH | **CRITICAL** | Protokol OT/ICS — paparan = risiko fisik. |
| **PPTP** 1723 | MEDIUM | **HIGH** | VPN lama dengan enkripsi lemah. |

### 8.4 Roll-up per host & prioritas
`analyzer.py` menjumlahkan kontribusi port → **skor & grade risiko per host**, lalu
membuat **daftar Prioritas** (urut severity menurun) yang tampil di
`priorities_pane.py` dan sheet **Prioritas** di Excel. Pesan untuk pemula bergaya:
*"3 hal mendesak: (1) RDP terbuka ke internet di 10.0.0.5 — batasi/aktifkan NLA; …"*
Setiap item menyertakan **rekomendasi tindakan** singkat.

---

## 9. Profil Siap-Pakai (Presets)

| Profil | Perintah Nmap | Untuk apa (ID) |
|---|---|---|
| **Quick Scan** | `-T4 -F` | Lihat cepat port umum terbuka. |
| **Quick + Versi** | `-sV -T4 -F` | Cepat + tahu layanan & versi. |
| **Intense Scan** | `-T4 -A -v` | Lengkap: port, versi, OS, skrip, traceroute. |
| **Intense (All Ports)** | `-p- -T4 -A -v` | Intense untuk semua 65k port. |
| **Intense (UDP)** | `-sU -sS -T4 -A -v` | Termasuk layanan UDP. |
| **Ping Sweep** | `-sn` | Petakan host hidup di subnet. |
| **Vuln Scan** | `-sV --script vuln` | Cari kerentanan umum (hati-hati). |
| **Stealth/Slow** | `-sS -T2 -f` | Pelan & sembunyi untuk lingkungan sensitif. |
| **Discovery** | `-sn -PR -PS21-23,80,443` | Penemuan host menyeluruh di LAN. |
| **Custom** | *(builder)* | Susun teknik & skrip sendiri. |

Profil bisa **disimpan & dibagikan** (My Profiles), tersimpan di config.

---

## 10. Desain GUI & Menu (dengan Hint Tiap Item)

### 10.1 Tata letak jendela utama

```
┌─ Abilithic Scan ───────────────────────────────────────────[ID/EN][◐]─┐
│  File   Scan   View   Tools   Help                                     │
├────────────────────────────────────────────────────────────────────────┤
│  Target: [ 192.168.1.0/24       ▼]   Profile: [ Intense Scan  ▼] [NSE…] │
│  Command: nmap -T4 -A -v 192.168.1.0/24            [ ▶ Start ] [ ⏸ ]    │
├──────────────┬─────────────────────────────────────────────────────────┤
│ Hosts        │  Ports  Details  NSE Output  Priorities  Topology        │
│ ┌──────────┐ │  ┌──────────────────────────────────────────────────┐   │
│ │●10.0.0.5 │ │  │ Port  State Service  Version    Criticality  Why  │   │
│ │  HIGH    │ │  │ 3389  open  ms-wbt    —          ●CRITICAL    🌐+RDP│  │
│ │●10.0.0.1 │ │  │ 445   open  smb       —          ●HIGH        SMB  │   │
│ │○10.0.0.9 │ │  │ 22    open  ssh       OpenSSH 8.9 ●LOW        ssh  │   │
│ └──────────┘ │  └──────────────────────────────────────────────────┘   │
├──────────────┴─────────────────────────────────────────────────────────┤
│ ▣ Log live ... [phase: nse]  ██████░░░ 68%  ETA 00:42   [ Cancel ]       │
├──────────────────────────────────────────────────────────────────────────┤
│ Hint: "CRITICAL: RDP terbuka ke internet — batasi akses / aktifkan NLA."  │
└──────────────────────────────────────────────────────────────────────────┘
```

Tab kanan: **Ports** (berwarna severity), **Details** (OS, uptime, traceroute, alasan
kritikalitas), **NSE Output** (hasil skrip rapi), **Priorities** (apa yang harus
diperhatikan dulu), **Topology** (peta jaringan dari traceroute).

### 10.2 Menu bar + hint (status bar, dua bahasa)

| Menu | Hint (ID) | Hint (EN) |
|---|---|---|
| **File ▸ New / Open / Save** | Mulai baru / buka / simpan hasil scan. | New / open / save scan. |
| **File ▸ Export ▸ Excel** | Laporan `.xlsx` rapi + sheet Prioritas. | Polished `.xlsx` + Priorities sheet. |
| **File ▸ Export ▸ HTML/JSON/CSV** | Bagikan, otomasi, atau spreadsheet mentah. | Share / automate / raw sheet. |
| **File ▸ Import Targets** | Muat daftar target dari `.txt`. | Load targets from `.txt`. |
| **Scan ▸ Start / Pause / Cancel** | Jalankan / jeda / hentikan scan. | Run / pause / stop. |
| **Scan ▸ Profile / Technique Builder** | Pilih preset / susun teknik. | Preset / build technique. |
| **Scan ▸ NSE Scripts** | Pilih skrip pemeriksaan mendalam. | Pick deep-check scripts. |
| **Scan ▸ Custom Flags** | Tambah flag Nmap manual (mahir). | Raw Nmap flags. |
| **View ▸ Theme / Language / Learning Mode** | Tema / bahasa / penjelasan tiap flag. | Theme / language / explain flags. |
| **Tools ▸ Npcap Status / Nmap Version** | Cek driver & versi mesin. | Driver & engine status. |
| **Tools ▸ Update NSE** | Segarkan indeks & DB CVE. | Refresh scripts & CVE DB. |
| **Tools ▸ Compare Scans** | Bandingkan dua hasil (diff). | Diff two scans. |
| **Help ▸ Quick Start / Licenses / Disclaimer / About** | Panduan / lisensi / etika / kredit. | Guide / licenses / ethics / credits. |

### 10.3 Mode Belajar & konsistensi hint
Learning Mode menampilkan flag yang dihasilkan + penjelasan + contoh, menyorot bagian
baru di command preview. Setiap kontrol punya `hint_key` (`gui/hints.py`) → status bar
& tooltip, diterjemahkan via i18n.

---

## 11. Model Data (Kontrak Versioned)

Mengikuti `core/models.py` Recon: dataclass berversi, `to_dict`/`from_dict` toleran.

```python
SCHEMA_VERSION = 1

class PortState(str, Enum):  OPEN, CLOSED, FILTERED, UNFILTERED, OPEN_FILTERED, CLOSED_FILTERED
class Protocol(str, Enum):   TCP, UDP, SCTP, IP
class Severity(str, Enum):   INFO, LOW, MEDIUM, HIGH, CRITICAL   # .rank 0..4

@dataclass
class Service:
    name=""; product=""; version=""; extrainfo=""; cpe: list[str]=[]; tunnel=""; method=""; conf=0

@dataclass
class ScriptResult:
    id=""; output=""; severity="INFO"; cve: list[str]=[]; kev: bool=False; elements: dict={}

@dataclass
class CriticalityContributor:        # ★ transparansi
    factor=""; weight=0; reason=""    # mis. ("exposure","+1","internet-facing")

@dataclass
class CriticalityBreakdown:          # ★ per port
    severity="INFO"; score=0; contributors: list[CriticalityContributor]=[]; advice=""

@dataclass
class Port:
    portid=0; protocol="tcp"; state="open"; reason=""
    service: Service=Service(); scripts: list[ScriptResult]=[]
    criticality: CriticalityBreakdown=CriticalityBreakdown()   # ★

@dataclass
class OSMatch:  name=""; accuracy=0; family=""; cpe: list[str]=[]

@dataclass
class Host:
    address=""; addrtype="ipv4"; mac=""; vendor=""; hostnames: list[str]=[]
    state="up"; reason=""; exposure="internal"          # internal|public (untuk konteks §8)
    ports: list[Port]=[]; os_matches: list[OSMatch]=[]
    uptime_seconds: int|None=None; distance: int|None=None; traceroute: list[dict]=[]
    risk_score=0; risk_grade="INFO"                     # roll-up

@dataclass
class PriorityItem:                  # ★ untuk pane & sheet Prioritas
    severity="HIGH"; host=""; port=0; title=""; advice=""

@dataclass
class ScanMeta:
    app_version=""; nmap_version=""; command=""; scan_args: list[str]=[]
    started_at=""; finished_at=""; duration_s=0.0; profile=""; locale="id"
    was_cancelled=False; elevated=False

@dataclass
class ScanResult:
    schema_version=SCHEMA_VERSION; scan_meta: ScanMeta=ScanMeta()
    hosts: list[Host]=[]; priorities: list[PriorityItem]=[]; summary: dict={}
    def to_dict(self)->dict: ...
    @staticmethod
    def from_dict(d)->"ScanResult": ...   # loader toleran (gaya Recon)
```

---

## 12. Laporan Excel yang Rapi (Fitur Unggulan)

Workbook `.xlsx` multi-sheet, berformat, siap presentasi (openpyxl) di
`reports/xlsx_report.py`.

| Sheet | Isi |
|---|---|
| **1 · Summary** | Header berlogo, target, profil, perintah & versi Nmap, waktu/durasi. Kartu metrik: host up/down, total port terbuka, **jumlah temuan per severity**. Chart batang/pie. |
| **2 · ★ Priorities** | **Daftar "apa yang harus diperhatikan dulu"**, urut CRITICAL→LOW: Severity, Host, Port, Masalah, **Rekomendasi tindakan**. Sheet pertama yang dibaca pemula. |
| **3 · Hosts** | Per host: IP, hostname, status, MAC/vendor, OS (+akurasi), paparan (publik/internal), jml port terbuka, **risk grade** (sel berwarna). |
| **4 · Open Ports** | Per port terbuka: Host, Port, Proto, Service, Product, Version, CPE, **Criticality** (berwarna), **Why/alasan**. Tabel inti. |
| **5 · Services** | Agregasi layanan & versi unik + jumlah host (inventaris/patch). |
| **6 · NSE / CVE** | Output skrip dirapikan: Host, Port, Script, Ringkasan, **CVE**, **KEV?**, Severity. |
| **7 · Appendix** | Perintah lengkap, host mati, error — audit & reproduksibilitas. |

**Formatting "rapi":** header brand ter-merge berlogo; **freeze panes** + **AutoFilter**;
lebar kolom auto-fit + wrap; **pewarnaan severity** (CRITICAL merah … INFO abu)
konsisten dengan GUI; **tabel ber-style** (zebra, sortable); chart di Summary;
**print-ready** (landscape, header/footer, area cetak); judul kolom mengikuti bahasa
aktif (ID/EN); metadata workbook terisi. CSV tetap ada sebagai fallback otomasi.

> Acuan teknik openpyxl: gunakan **skill `xlsx`** proyek ini saat membangun sheet,
> tabel, conditional formatting, dan chart.

---

## 13. Performa & Akurasi (Lebih Cepat, Tetap Akurat)

Tujuan: **lebih cepat dari Zenmap default tanpa kehilangan akurasi**.

1. **Scan dua-fase (cerdas).**
   - *Fase A — Discovery cepat*: temukan port terbuka dulu (`-sS --min-rate` /
     `--top-ports` atau `-p-`) tanpa `-sV`/NSE.
   - *Fase B — Deep (terarah)*: jalankan `-sV`, `-O`, dan NSE **hanya pada port yang
     terbukti terbuka** dari Fase A. Ini memangkas waktu drastis untuk range besar
     karena probe mahal tidak dihambur ke port tertutup.
   - Diimplementasikan oleh `command_builder` (menyusun perintah Fase B dari hasil
     Fase A); untuk target tunggal cukup satu perintah karena Nmap sudah membatasi
     `-sV`/NSE ke port terbuka.
2. **Timing pintar, bukan asal cepat.** Default **`-T4`** (bukan `-T5`, yang dapat
   menurunkan akurasi). Untuk range besar, tambah **`--min-rate`** sebagai lantai
   laju + paralelisme host-group, sambil menjaga `--max-retries` wajar.
3. **Akurasi terjaga.** `--version-intensity` seimbang; `--max-retries` tidak terlalu
   kecil agar host lambat tak salah dianggap mati; **tampilkan confidence** (akurasi
   OS, conf versi) sehingga pemula tahu tingkat keyakinan.
4. **Adaptif menurut target.** LAN → **ARP ping** (tercepat & akurat). Host yang blok
   ping → sarankan `-Pn`. App memilih default cerdas berdasarkan tipe target.
5. **Streaming, bukan menunggu.** Hasil & progress tampil real-time dari XML; ETA
   nyata dari `<taskprogress>`.
6. **Roadmap akselerasi:** integrasi **masscan** opsional untuk pre-sweep ultra-cepat
   lalu Nmap untuk akurasi (lihat §18) — perlu kajian lisensi/bundling.

---

## 14. Internasionalisasi (ID / EN)

Identik Recon: simpan **KEY** di data, resolve teks saat tampil. `Translator.t(key)`
fallback ke `en`. Default `id`. Bahasa memengaruhi UI, hint, judul kolom Excel/HTML,
dan teks rekomendasi kritikalitas.

```json
{ "technique.sS.hint": "Scan cepat & sopan; tak menyelesaikan koneksi.",
  "crit.rdp.reason": "Remote Desktop; target favorit ransomware bila terbuka ke internet.",
  "report.col.criticality": "Kritikalitas", "severity.CRITICAL": "Kritis" }
```

---

## 15. Build, Packaging & Single .exe

**PyInstaller** → satu `AbilithicScan.exe`, `console=False`, ikon brand,
`version_info.txt`, GitHub Actions build + checksum (pola Recon).

```python
datas = [
    ("abilithic_scan/data/nmap",    "abilithic_scan/data/nmap"),     # binary + DB + scripts NSE
    ("abilithic_scan/data/catalog", "abilithic_scan/data/catalog"),
    ("abilithic_scan/data/knowledge","abilithic_scan/data/knowledge"),# port_criticality.json, kev.json
    ("abilithic_scan/i18n/locales", "abilithic_scan/i18n/locales"),
    ("assets", "assets"),
    # Npcap: di-fetch saat first-run (lihat §5.4)
]
hiddenimports = ["openpyxl", "lxml"]
excludes = ["tkinter", "matplotlib", "PyQt5", "PyQt6"]
```

`requirements.txt`: `PySide6>=6.6.0`, `openpyxl>=3.1.0`, `lxml>=5.0.0`.

**Hak admin (UAC):** SYN/UDP/OS butuh admin; app menawarkan *relaunch elevated*; jika
ditolak, turun ke `-sT` tanpa admin + banner ramah.

---

## 16. Struktur Folder Proyek

```
Project_2-Scan/
└── abilithic-scan/
    ├── abilithic_scan/         # paket utama (§4)
    ├── assets/  tests/  .github/workflows/build.yml
    ├── abilithic-scan.spec  build.bat  main.py
    ├── requirements.txt / requirements-dev.txt  version_info.txt
    ├── README.md  CHANGELOG.md  DISCLAIMER.md
    ├── THIRD-PARTY-LICENSES.md  LICENSE
```

Konsisten dengan `Project_1-Recon/abilithic-recon/`.

---

## 17. Keamanan, Etika & Consent

- **Gerbang consent** sebelum scan aktif: "Saya berwenang men-scan target ini."
  Teknik/skrip `intrusive/brute` → konfirmasi; `dos/exploit` → konfirmasi dua langkah
  + badge 🛑.
- **DISCLAIMER.md** & **Help ▸ Disclaimer**: hanya untuk pengujian sah & edukasi.
- **Tanpa telemetry/eksfiltrasi**; semua lokal. Auto-setup Npcap hanya unduh installer
  resmi (ditampilkan ke pengguna). Skrip kategori `external` diberi peringatan privasi.
- **Default sopan** (`-T4`), tidak membanjiri jaringan.
- **Audit trail**: perintah persis + versi Nmap tercatat di hasil & sheet Appendix.

---

## 18. Roadmap

- **v1.0** — Semua teknik §6, **NSE penuh** §7, **mesin kritikalitas** §8, parser XML
  streaming, tabel live berwarna, sheet **Prioritas**, **Excel/HTML/JSON/CSV**, ID/EN,
  single `.exe`, auto-setup Npcap, Learning Mode, scan dua-fase.
- **v1.1** — *Compare Scans* (diff port baru/hilang), *Topology view* interaktif,
  scheduler, resume/pause UI, import target lanjutan.
- **v1.2** — Ringkasan CVE/KEV diperkaya di Excel, ekspor **PDF**, template laporan
  berlogo perusahaan, profil tim, integrasi **masscan** opsional (pre-sweep cepat).
- **v2.0 (Abilithic Atlas)** — gabung Recon + Scan: domain → subdomain → host → port →
  layanan → kerentanan dalam satu alur & laporan terpadu; riwayat & tren.

---

## 19. Ide Tambahan / Pembeda (Value-Add)

1. **Mesin Kritikalitas transparan (§8)** — fakta Nmap diubah jadi prioritas yang
   bisa ditindaklanjuti, dengan *alasan* yang bisa dibaca pemula.
2. **Sheet Prioritas di Excel** — "apa yang harus diperbaiki dulu" untuk manajemen.
3. **Command preview + Learning Mode** — alat yang mengajari, bukan kotak hitam.
4. **NSE Script Browser berkategori + tujuan** — 600+ skrip jadi mudah dipilih.
5. **Korelasi CVE + CISA KEV** — naikkan otomatis yang sedang dieksploitasi liar.
6. **Scan dua-fase** — lebih cepat, tetap akurat (§13).
7. **Compare/Diff scan** — deteksi port yang *baru terbuka* sebagai sinyal dini.
8. **Topology view** — peta jaringan dari traceroute, visual untuk pemula.
9. **Safe-by-default + UAC fallback** — tak pernah "gagal misterius".
10. **Pluggable JSON** — teknik/preset/skrip/kritikalitas tambah via katalog, tanpa
    ubah engine (paralel pola `BaseSource` Recon).
11. **Satu keluarga dengan Recon** — menuju *Abilithic Atlas*.

---

## 20. Tinjauan Konsep: Celah yang Ditambal & Peningkatan

Hasil tinjauan ulang v0.1 → v0.2. **Yang ditemukan kurang dan kini ditambahkan:**

| # | Celah / kekurangan di v0.1 | Perbaikan di v0.2 |
|---|---|---|
| 1 | **Tidak ada penilaian risiko per port** — pemula tak tahu mana yang penting. | **Mesin Kritikalitas §8** + knowledge base + roll-up + sheet Prioritas. |
| 2 | NSE hanya disinggung sekilas. | **Bagian NSE penuh §7**: 14 kategori, script browser, argumen, CVE, skrip kustom, gating. |
| 3 | Tak ada strategi kecepatan vs akurasi. | **§13 Performa & Akurasi** (scan dua-fase, timing pintar, confidence). |
| 4 | **IPv6** belum disebut. | `-6` ditambahkan (§6.7) + `addrtype` di model. |
| 5 | Tak ada **exclude / resume / input-list / random**. | `--exclude(file)`, `--resume`, `-iL`, `-iR` (§6.7). |
| 6 | Tak ada **Pause** (hanya Cancel). | Tombol **Pause/Resume** di command bar (§10). |
| 7 | Konteks paparan diabaikan (RDP internal vs publik dinilai sama). | Field **`exposure`** (public/internal) sebagai faktor kritikalitas (§8.2/§11). |
| 8 | Penanganan **hasil kosong / error** belum dijelaskan. | Banner ramah & status (§5.3 fallback, §17), Appendix error di Excel. |
| 9 | **CVE/KEV** tak terhubung ke output. | `vulners`/`vulscan` → Finding → eskalasi; KEV → CRITICAL (§7.4/§8). |
| 10 | Simpan **output native Nmap** (audit) tak ada. | `-oA/-oN/-oG` opsional (§6.7) + sheet Appendix. |
| 11 | Akurasi/confidence tak ditampilkan. | Tampilkan akurasi OS & conf versi (§13). |

**Logic yang diperbaiki/diperjelas:**
- **Kritikalitas harus sadar-konteks & transparan** — bukan label tetap. "RDP" tidak
  selalu CRITICAL; menjadi CRITICAL bila **internet-facing** atau ada CVE/KEV. Setiap
  nilai menyimpan kontributor + alasan (dapat dijelaskan, dapat dikalibrasi via config).
- **NSE di fase deep** — skrip hanya jalan pada port terbuka relevan → akurat & cepat.
- **Severity final = max(base, evidence) + modifier**, lalu di-clamp — mencegah temuan
  NSE "menenggelamkan" base, dan sebaliknya.
- **Reproduksibilitas** — versi Nmap + perintah persis disimpan; penting karena hasil
  bisa berbeda antar versi Nmap.

**Masih terbuka untuk diputuskan (bukan blocker):**
- Bundling penuh vs first-run fetch Npcap (lihat §5.4) — keputusan lisensi.
- Integrasi masscan (kecepatan ekstra) — kajian lisensi (masscan = AGPL).
- Sumber KEV offline + frekuensi update DB CVE.

---

## 21. Lampiran: Pemetaan Flag Nmap

`command_builder.py` menerima `ScanSpec` → `argv`. Preview = perintah nyata.

```python
@dataclass
class ScanSpec:
    targets: list[str]                 # IP/host/CIDR/range/IPv6 (tervalidasi)
    exclude: list[str] = []            # --exclude / --excludefile
    discovery: list[str] = []          # -Pn | -sn | -PR | -n …
    scan_type: str = "-sS"             # §6.2 (fallback -sT bila tanpa Npcap)
    ipv6: bool = False                 # -6
    ports: str = "--top-ports 1000"    # -p- | -p 22,80 | -F | --open
    service_detect: bool = False       # -sV ; version_intensity: int|None
    os_detect: bool = False            # -O ; traceroute: bool ; aggressive: bool  # -A
    timing: str = "-T4"                # + min_rate/max_retries/host_timeout (opsional)
    nse: list[str] = []                # ekspresi --script (kategori/nama/boolean)
    nse_args: str = ""                 # --script-args
    evasion: list[str] = []            # -f -D -g --spoof-mac …
    two_phase: bool = True             # §13 (deep hanya pada port terbuka)
    save_native: str = ""              # -oA/-oN/-oG (opsional)
    extra_flags: list[str] = []        # Custom Flags (mahir)
    output_xml_stdout: bool = True     # -oX -  (selalu, untuk parsing)

def build(spec: ScanSpec) -> list[str]: ...   # satu-satunya sumber kebenaran
```

---

<div align="center">

### 👤 Konsep oleh **Abil Khosim** — *Cybersecurity Specialist*

*Abilithic Scan* — bagian dari keluarga Abilithic (Recon · Scan · Atlas).
**Security, built like stone.** 🛡️

</div>
