"""Table model for the open-ports view, with severity colouring & sort/filter."""
from __future__ import annotations

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QColor

from ..core.models import sev_rank
from .theme import SEV_COLORS

# (header_key, attribute getter)
COLUMNS = ["col.host", "col.port", "col.proto", "col.service",
           "col.version", "col.criticality"]


class PortRow:
    __slots__ = ("host", "portid", "proto", "service", "version", "severity",
                 "why", "advice", "host_obj", "port_obj")

    def __init__(self, host, port):
        self.host = host.address or host.primary_name()
        self.portid = port.portid
        self.proto = port.protocol
        self.service = port.service.name
        self.version = port.service.label()
        self.severity = port.criticality.severity
        self.why = "; ".join(c.reason for c in port.criticality.contributors)
        self.advice = port.criticality.advice
        self.host_obj = host
        self.port_obj = port


class PortTableModel(QAbstractTableModel):
    def __init__(self, tr):
        super().__init__()
        self._tr = tr
        self._rows: list = []

    def set_result(self, result):
        self.beginResetModel()
        self._rows = [PortRow(h, p) for h in result.hosts for p in h.open_ports()]
        self.endResetModel()

    def clear(self):
        self.beginResetModel()
        self._rows = []
        self.endResetModel()

    def row_at(self, r):
        return self._rows[r] if 0 <= r < len(self._rows) else None

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return len(COLUMNS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._tr(COLUMNS[section])
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = self._rows[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return row.host
            if col == 1: return row.portid
            if col == 2: return row.proto
            if col == 3: return row.service
            if col == 4: return row.version
            if col == 5: return self._tr(f"severity.{row.severity}")
        if role == Qt.UserRole:
            # used for proper numeric/severity sorting
            if col == 1: return row.portid
            if col == 5: return sev_rank(row.severity)
            return self.data(index, Qt.DisplayRole)
        if role == Qt.ToolTipRole:
            return row.why
        if role == Qt.ForegroundRole and col == 5:
            return QColor(SEV_COLORS.get(row.severity, "#8c97a8"))
        if role == Qt.TextAlignmentRole and col in (1, 2, 5):
            return int(Qt.AlignCenter)
        return None


class PortProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.setSortRole(Qt.UserRole)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(-1)  # all columns
