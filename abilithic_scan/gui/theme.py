"""Brand palette + Qt stylesheets (dark / light). Matches Abilithic Recon."""
from __future__ import annotations

CHARCOAL = "#0c1118"
SLATE = "#161e29"
SLATE2 = "#1d2734"
LINE = "#26303f"
TEXT = "#e7edf5"
MUTED = "#8c97a8"
ACCENT = "#48f3d2"
ACCENT_DK = "#0fb497"

SEV_COLORS = {
    "CRITICAL": "#ff5c7a",
    "HIGH": "#ff9f43",
    "MEDIUM": "#ffd166",
    "LOW": "#62d5b8",
    "INFO": "#8c97a8",
}

# Readable text colour to place ON each severity badge background.
SEV_TEXT = {
    "CRITICAL": "#ffffff",
    "HIGH": "#4a2500",
    "MEDIUM": "#4a3b00",
    "LOW": "#06352b",
    "INFO": "#11202e",
}

_DARK = f"""
QMainWindow, QWidget {{ background:{CHARCOAL}; color:{TEXT};
  font-family:'Segoe UI','Roboto',Arial,sans-serif; font-size:13px; }}
QMenuBar {{ background:{SLATE}; color:{TEXT}; padding:2px; }}
QMenuBar::item {{ padding:6px 10px; border-radius:6px; }}
QMenuBar::item:selected {{ background:{SLATE2}; }}
QMenu {{ background:{SLATE}; color:{TEXT}; border:1px solid {LINE}; }}
QMenu::item {{ padding:6px 22px; }}
QMenu::item:selected {{ background:{ACCENT_DK}; color:{CHARCOAL}; }}
QLineEdit {{ background:{SLATE2}; border:1px solid {LINE}; border-radius:8px;
  padding:8px 10px; color:{TEXT}; selection-background-color:{ACCENT_DK}; }}
QLineEdit:focus {{ border:1px solid {ACCENT}; }}
QLineEdit:read-only {{ color:{MUTED}; }}
QPushButton {{ background:{ACCENT}; color:{CHARCOAL}; border:none; border-radius:8px;
  padding:8px 16px; font-weight:600; }}
QPushButton:hover {{ background:{ACCENT_DK}; color:{TEXT}; }}
QPushButton:disabled {{ background:{LINE}; color:{MUTED}; }}
QPushButton#secondary {{ background:{SLATE2}; color:{TEXT}; border:1px solid {LINE}; }}
QPushButton#secondary:hover {{ border:1px solid {ACCENT}; }}
QComboBox {{ background:{SLATE2}; border:1px solid {LINE}; border-radius:8px; padding:6px 10px; }}
QComboBox:hover {{ border:1px solid {ACCENT}; }}
QComboBox QAbstractItemView {{ background:{SLATE}; selection-background-color:{ACCENT_DK};
  selection-color:{CHARCOAL}; }}
QFrame#card {{ background:{SLATE}; border:1px solid {LINE}; border-radius:12px; }}
QLabel#cardNum {{ font-size:22px; font-weight:700; }}
QLabel#cardLbl {{ color:{MUTED}; font-size:10px; }}
QTableView {{ background:{SLATE}; gridline-color:{LINE}; border:1px solid {LINE};
  border-radius:10px; selection-background-color:{ACCENT_DK}; selection-color:{CHARCOAL}; }}
QHeaderView::section {{ background:{SLATE2}; color:{MUTED}; border:none;
  border-bottom:1px solid {LINE}; padding:8px; }}
QListWidget {{ background:{SLATE}; border:1px solid {LINE}; border-radius:10px; padding:4px; }}
QListWidget::item {{ padding:8px; border-radius:6px; }}
QListWidget::item:selected {{ background:{ACCENT_DK}; color:{CHARCOAL}; }}
QTabWidget::pane {{ border:1px solid {LINE}; border-radius:10px; }}
QTabBar::tab {{ background:{SLATE}; color:{MUTED}; padding:8px 16px; border:1px solid {LINE};
  border-bottom:none; border-top-left-radius:8px; border-top-right-radius:8px; }}
QTabBar::tab:selected {{ background:{SLATE2}; color:{ACCENT}; }}
QTextEdit, QPlainTextEdit, QTextBrowser {{ background:{SLATE}; border:1px solid {LINE};
  border-radius:10px; padding:6px; }}
QProgressBar {{ background:{SLATE2}; border:1px solid {LINE}; border-radius:8px; text-align:center;
  color:{TEXT}; height:18px; }}
QProgressBar::chunk {{ background:{ACCENT}; border-radius:7px; }}
QStatusBar {{ background:{SLATE}; color:{MUTED}; }}
QSplitter::handle {{ background:{LINE}; }}
QCheckBox {{ spacing:8px; }}
QScrollBar:vertical {{ background:{CHARCOAL}; width:10px; }}
QScrollBar::handle:vertical {{ background:{LINE}; border-radius:5px; }}
QToolTip {{ background:{SLATE2}; color:{TEXT}; border:1px solid {ACCENT}; padding:6px; }}
"""

_LIGHT = """
QMainWindow, QWidget { background:#f4f6fa; color:#1b2533;
  font-family:'Segoe UI','Roboto',Arial,sans-serif; font-size:13px; }
QMenuBar { background:#fff; } QMenuBar::item:selected { background:#e8edf4; }
QMenu { background:#fff; border:1px solid #e0e6ee; }
QMenu::item:selected { background:#0fb497; color:#fff; }
QLineEdit { background:#fff; border:1px solid #cdd5e0; border-radius:8px; padding:8px 10px; }
QLineEdit:focus { border:1px solid #0fb497; }
QPushButton { background:#0fb497; color:#fff; border:none; border-radius:8px; padding:8px 16px; font-weight:600; }
QPushButton:hover { background:#0c9a81; }
QPushButton:disabled { background:#cdd5e0; color:#8c97a8; }
QPushButton#secondary { background:#fff; color:#1b2533; border:1px solid #cdd5e0; }
QComboBox { background:#fff; border:1px solid #cdd5e0; border-radius:8px; padding:6px 10px; }
QFrame#card { background:#fff; border:1px solid #e0e6ee; border-radius:12px; }
QTableView { background:#fff; gridline-color:#e0e6ee; border:1px solid #e0e6ee; border-radius:10px;
  selection-background-color:#0fb497; selection-color:#fff; }
QHeaderView::section { background:#eef1f6; color:#5a6675; border:none; border-bottom:1px solid #e0e6ee; padding:8px; }
QListWidget, QTextEdit, QPlainTextEdit, QTextBrowser { background:#fff; border:1px solid #e0e6ee; border-radius:10px; }
QTabBar::tab { background:#eef1f6; color:#5a6675; padding:8px 16px; }
QTabBar::tab:selected { background:#fff; color:#0fb497; }
QProgressBar { background:#eef1f6; border:1px solid #e0e6ee; border-radius:8px; text-align:center; height:18px; }
QProgressBar::chunk { background:#0fb497; border-radius:7px; }
QStatusBar { background:#fff; color:#5a6675; }
QToolTip { background:#fff; color:#1b2533; border:1px solid #0fb497; padding:6px; }
"""


def stylesheet(theme: str) -> str:
    return _LIGHT if theme == "light" else _DARK
