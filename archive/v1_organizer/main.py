"""Application entrypoint."""

from fivem_vehicle_tool.ui import main


if __name__ == "__main__":
    main()
"""
FiveM Asset Organizer
=====================
Organiseert FiveM voertuig resources in een nette structuur per categorie.

Installatie:
    pip install PyQt6

Gebruik:
    python fivem_asset_organizer.py
"""

import sys
import os
import re
import shutil
import zipfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QSplitter, QProgressBar, QTextEdit, QComboBox, QCheckBox, QGroupBox,
    QScrollArea, QFrame, QDialog, QDialogButtonBox, QMessageBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QMimeData, QUrl, QTimer, QSize
)
from PyQt6.QtGui import (
    QDragEnterEvent, QDropEvent, QColor, QFont, QPalette, QIcon,
    QPixmap, QPainter, QBrush, QLinearGradient
)

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTEN
# ─────────────────────────────────────────────────────────────────────────────

VERSION = "1.0.0"

# FiveM vehicleClass waarden → categorie naam
VEHICLE_CLASS_MAP = {
    "0": "compact",
    "1": "sedan",
    "2": "suv",
    "3": "coupe",
    "4": "muscle",
    "5": "sports_classic",
    "6": "sports",
    "7": "super",
    "8": "motorcycle",
    "9": "offroad",
    "10": "industrial",
    "11": "utility",
    "12": "van",
    "13": "bicycle",
    "14": "boat",
    "15": "helicopter",
    "16": "plane",
    "17": "service",
    "18": "emergency",
    "19": "military",
    "20": "commercial",
    "21": "train",
}

# Tekst labels → vehicleClass nummers (voor display)
CLASS_LABELS = {v: k for k, v in VEHICLE_CLASS_MAP.items()}

ALL_CATEGORIES = sorted(set(VEHICLE_CLASS_MAP.values())) + ["_unknown"]

# Bestands-extensies per type
STREAM_EXTENSIONS = {".yft", ".ytd", ".ycd", ".ymap", ".ytyp", ".ydd", ".yld", ".yvr"}
META_EXTENSIONS   = {".meta", ".xml"}
MANIFEST_FILES    = {"fxmanifest.lua", "__resource.lua"}

# Kleurenschema (donker thema)
COLORS = {
    "bg":         "#0f1117",
    "surface":    "#1a1d27",
    "surface2":   "#22263a",
    "border":     "#2d3250",
    "accent":     "#5b8af5",
    "accent2":    "#7c5bf5",
    "success":    "#3ecf8e",
    "warning":    "#f5a623",
    "error":      "#f55b5b",
    "text":       "#e8eaf6",
    "text_dim":   "#7b82a8",
    "unknown":    "#f5a623",
}

STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
}}
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
QGroupBox {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding: 8px;
    font-weight: bold;
    color: {COLORS['accent']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}
QPushButton {{
    background-color: {COLORS['surface2']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 32px;
}}
QPushButton:hover {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
    color: white;
}}
QPushButton:pressed {{
    background-color: {COLORS['accent2']};
}}
QPushButton:disabled {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_dim']};
    border-color: {COLORS['border']};
}}
QPushButton#primary {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    font-size: 14px;
    min-height: 40px;
    border-radius: 8px;
}}
QPushButton#primary:hover {{
    background-color: {COLORS['accent2']};
}}
QPushButton#success {{
    background-color: {COLORS['success']};
    color: #0f1117;
    border: none;
    font-size: 14px;
    min-height: 40px;
    border-radius: 8px;
}}
QPushButton#success:hover {{
    background-color: #2eaf74;
}}
QPushButton#danger {{
    background-color: {COLORS['error']};
    color: white;
    border: none;
}}
QLineEdit {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {COLORS['text']};
    selection-background-color: {COLORS['accent']};
}}
QLineEdit:focus {{
    border-color: {COLORS['accent']};
}}
QTreeWidget {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    alternate-background-color: {COLORS['surface2']};
    outline: none;
}}
QTreeWidget::item {{
    padding: 4px 2px;
    border: none;
}}
QTreeWidget::item:selected {{
    background-color: {COLORS['accent']};
    color: white;
}}
QTreeWidget::item:hover {{
    background-color: {COLORS['surface2']};
}}
QTreeWidget QHeaderView::section {{
    background-color: {COLORS['surface2']};
    border: 1px solid {COLORS['border']};
    padding: 6px;
    font-weight: bold;
    color: {COLORS['text_dim']};
}}
QTableWidget {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    gridline-color: {COLORS['border']};
    alternate-background-color: {COLORS['surface2']};
    outline: none;
}}
QTableWidget::item {{
    padding: 4px 8px;
}}
QTableWidget::item:selected {{
    background-color: {COLORS['accent']};
    color: white;
}}
QHeaderView::section {{
    background-color: {COLORS['surface2']};
    border: 1px solid {COLORS['border']};
    padding: 8px;
    font-weight: bold;
    color: {COLORS['text_dim']};
}}
QTextEdit {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    color: {COLORS['text']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}
QProgressBar {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    text-align: center;
    color: {COLORS['text']};
    min-height: 20px;
}}
QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 5px;
}}
QComboBox {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    color: {COLORS['text']};
    min-height: 28px;
}}
QComboBox:hover {{
    border-color: {COLORS['accent']};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['surface2']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['accent']};
    color: {COLORS['text']};
}}
QCheckBox {{
    spacing: 8px;
    color: {COLORS['text']};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background-color: {COLORS['surface']};
}}
QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 0 8px 8px 8px;
    background-color: {COLORS['surface']};
}}
QTabBar::tab {{
    background-color: {COLORS['surface2']};
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    padding: 8px 20px;
    margin-right: 2px;
    border-radius: 6px 6px 0 0;
    color: {COLORS['text_dim']};
}}
QTabBar::tab:selected {{
    background-color: {COLORS['surface']};
    color: {COLORS['accent']};
    border-color: {COLORS['border']};
}}
QScrollBar:vertical {{
    background-color: {COLORS['surface']};
    width: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['accent']};
}}
QScrollBar:horizontal {{
    background-color: {COLORS['surface']};
    height: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal {{
    background-color: {COLORS['border']};
    border-radius: 5px;
}}
QLabel#title {{
    font-size: 22px;
    font-weight: bold;
    color: {COLORS['accent']};
    font-family: 'Consolas', monospace;
}}
QLabel#subtitle {{
    font-size: 12px;
    color: {COLORS['text_dim']};
}}
QLabel#badge_unknown {{
    background-color: {COLORS['warning']};
    color: #0f1117;
    border-radius: 10px;
    padding: 2px 8px;
    font-weight: bold;
    font-size: 11px;
}}
QLabel#badge_ok {{
    background-color: {COLORS['success']};
    color: #0f1117;
    border-radius: 10px;
    padding: 2px 8px;
    font-weight: bold;
    font-size: 11px;
}}
QFrame#separator {{
    background-color: {COLORS['border']};
    max-height: 1px;
}}
"""

# ─────────────────────────────────────────────────────────────────────────────
#  DATA KLASSEN
# ─────────────────────────────────────────────────────────────────────────────

class VehicleInfo:
    """Representeert 1 gedetecteerd voertuig."""
    def __init__(self, name: str, source_dir: Path):
        self.name = name                        # spawn naam / folder naam (genormaliseerd)
        self.original_name = name               # originele naam
        self.source_dir = source_dir            # originele map
        self.stream_files: list[Path] = []      # .yft, .ytd, etc.
        self.meta_files: list[Path] = []        # .meta, .xml
        self.manifest_files: list[Path] = []    # fxmanifest.lua / __resource.lua
        self.detected_category: Optional[str] = None   # uit vehicles.meta
        self.assigned_category: Optional[str] = None   # handmatig of auto
        self.issues: list[str] = []             # waarschuwingen
        self.vehicle_class_raw: Optional[str] = None   # raw class nummer

    @property
    def category(self) -> str:
        return self.assigned_category or self.detected_category or "_unknown"

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def is_unknown(self) -> bool:
        return self.category == "_unknown"


# ─────────────────────────────────────────────────────────────────────────────
#  SCANNER
# ─────────────────────────────────────────────────────────────────────────────

class VehicleScanner:
    """Scant een map recursief en detecteert voertuig resources."""

    def __init__(self, root: Path):
        self.root = root
        self.vehicles: list[VehicleInfo] = []
        self.errors: list[str] = []

    def scan(self, progress_callback=None) -> list[VehicleInfo]:
        self.vehicles = []
        self.errors = []

        # Zoek alle potentiële resource folders
        resource_dirs = self._find_resource_dirs(self.root)

        total = len(resource_dirs)
        for i, rdir in enumerate(resource_dirs):
            if progress_callback:
                progress_callback(int((i / max(total, 1)) * 100), rdir.name)
            vehicle = self._parse_resource(rdir)
            if vehicle:
                self.vehicles.append(vehicle)

        return self.vehicles

    def _find_resource_dirs(self, root: Path) -> list[Path]:
        """Vindt alle mappen die een fxmanifest.lua of __resource.lua bevatten."""
        result = []
        try:
            for item in root.rglob("*"):
                if item.is_file() and item.name.lower() in MANIFEST_FILES:
                    result.append(item.parent)
        except PermissionError as e:
            self.errors.append(str(e))
        # Dedupliceer
        seen = set()
        unique = []
        for p in result:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    def _parse_resource(self, rdir: Path) -> Optional[VehicleInfo]:
        """Parseert 1 resource folder naar een VehicleInfo object."""
        name = self._normalize_name(rdir.name)
        vehicle = VehicleInfo(name=name, source_dir=rdir)
        vehicle.original_name = rdir.name

        # Categoriseer bestanden
        for f in rdir.rglob("*"):
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            fname = f.name.lower()

            if fname in MANIFEST_FILES:
                vehicle.manifest_files.append(f)
            elif ext in STREAM_EXTENSIONS:
                vehicle.stream_files.append(f)
            elif ext in META_EXTENSIONS:
                vehicle.meta_files.append(f)

        # Probeer categorie te detecteren uit vehicles.meta
        self._detect_category(vehicle)

        # Valideer
        self._validate(vehicle)

        return vehicle

    def _detect_category(self, vehicle: VehicleInfo):
        """Leest vehicleClass uit vehicles.meta."""
        for mf in vehicle.meta_files:
            if "vehicles" in mf.name.lower() and mf.suffix.lower() == ".meta":
                try:
                    tree = ET.parse(mf)
                    root = tree.getroot()

                    # Zoek vehicleClass element
                    for elem in root.iter("vehicleClass"):
                        text = elem.text.strip() if elem.text else ""
                        # Kan zijn "VC_SUV" of gewoon een getal
                        if text.startswith("VC_"):
                            vc_name = text[3:].lower()
                            # Map naar onze categorieën
                            vehicle.detected_category = self._vc_to_category(vc_name)
                            vehicle.vehicle_class_raw = text
                            return
                        elif text.isdigit():
                            vehicle.detected_category = VEHICLE_CLASS_MAP.get(text, "_unknown")
                            vehicle.vehicle_class_raw = text
                            return
                except Exception:
                    pass  # Corrupte XML, skip

    def _vc_to_category(self, vc: str) -> str:
        """Converteert VC_SUV stijl naam naar categorie."""
        mapping = {
            "compact": "compact",
            "sedan": "sedan",
            "suv": "suv",
            "coupe": "coupe",
            "muscle": "muscle",
            "sportsclassic": "sports_classic",
            "sports": "sports",
            "super": "super",
            "motorcycle": "motorcycle",
            "offroad": "offroad",
            "industrial": "industrial",
            "utility": "utility",
            "van": "van",
            "bicycle": "bicycle",
            "boat": "boat",
            "helicopter": "helicopter",
            "plane": "plane",
            "service": "service",
            "emergency": "emergency",
            "military": "military",
            "commercial": "commercial",
            "train": "train",
        }
        return mapping.get(vc, "_unknown")

    def _normalize_name(self, name: str) -> str:
        """Normaliseert bestandsnamen: lowercase, spaties → underscore, speciale tekens eruit."""
        name = name.lower()
        name = re.sub(r"[\s\-]+", "_", name)
        name = re.sub(r"[^a-z0-9_]", "", name)
        name = re.sub(r"_+", "_", name).strip("_")
        return name or "vehicle"

    def _validate(self, vehicle: VehicleInfo):
        """Voegt waarschuwingen toe voor veelvoorkomende problemen."""
        if not vehicle.stream_files:
            vehicle.issues.append("⚠ Geen stream bestanden gevonden (.yft/.ytd)")
        if not vehicle.meta_files:
            vehicle.issues.append("⚠ Geen meta bestanden gevonden")
        if not any("vehicles" in f.name.lower() for f in vehicle.meta_files):
            vehicle.issues.append("⚠ Geen vehicles.meta gevonden")
        if not any("handling" in f.name.lower() for f in vehicle.meta_files):
            vehicle.issues.append("⚠ Geen handling.meta gevonden")
        if vehicle.original_name != vehicle.name:
            vehicle.issues.append(f"📝 Naam genormaliseerd: '{vehicle.original_name}' → '{vehicle.name}'")


# ─────────────────────────────────────────────────────────────────────────────
#  FXMANIFEST GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_fxmanifest(category: str, vehicles: list[VehicleInfo]) -> str:
    """Genereert een correcte fxmanifest.lua voor een categorie resource."""

    meta_entries = []
    for v in vehicles:
        for mf in v.meta_files:
            rel = f"meta/{mf.name}"
            meta_type = _detect_meta_type(mf.name)
            if meta_type:
                meta_entries.append((rel, meta_type))

    # Bouw manifest
    lines = [
        "fx_version 'cerulean'",
        "game 'gta5'",
        "",
        f"name '{category}_vehicles'",
        f"description 'FiveM vehicle resource - {category}'",
        f"version '1.0.0'",
        "",
        "-- Stream bestanden (modellen & textures)",
        "files {",
    ]

    # Voeg stream wildcard toe
    lines.append("    'stream/**'")
    lines.append("}")
    lines.append("")

    # Data files per type
    data_groups = {}
    for rel, meta_type in meta_entries:
        data_groups.setdefault(meta_type, []).append(rel)

    for meta_type, files in sorted(data_groups.items()):
        lines.append(f"-- {meta_type}")
        lines.append(f"data_file '{meta_type}' {{")
        for f in sorted(files):
            lines.append(f"    '{f}',")
        lines.append("}")
        lines.append("")

    return "\n".join(lines)


def _detect_meta_type(filename: str) -> Optional[str]:
    """Detecteert het data_file type op basis van de bestandsnaam."""
    fn = filename.lower()
    if "vehicles" in fn:
        return "VEHICLE_METADATA_FILE"
    elif "handling" in fn:
        return "HANDLING_FILE"
    elif "carcols" in fn:
        return "CARCOLS_FILE"
    elif "carvariations" in fn:
        return "VEHICLE_VARIATION_FILE"
    elif "vehiclelayouts" in fn:
        return "VEHICLE_LAYOUTS_FILE"
    elif "contentunlocks" in fn:
        return "CONTENT_UNLOCKING_META_FILE"
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  ORGANIZER (WORKER THREAD)
# ─────────────────────────────────────────────────────────────────────────────

class OrganizerWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)  # resultaat statistieken
    error = pyqtSignal(str)

    def __init__(self, vehicles: list[VehicleInfo], output_dir: Path, dry_run: bool, make_backup: bool, source_dir: Path):
        super().__init__()
        self.vehicles = vehicles
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.make_backup = make_backup
        self.source_dir = source_dir

    def run(self):
        try:
            stats = {
                "total": len(self.vehicles),
                "processed": 0,
                "unknown": 0,
                "errors": [],
                "backup_path": None,
                "categories": {},
            }

            # 1. Backup
            if self.make_backup and not self.dry_run:
                self.progress.emit(0, "Backup maken...")
                backup_path = self._make_backup()
                stats["backup_path"] = str(backup_path)

            # 2. Groepeer per categorie
            categories: dict[str, list[VehicleInfo]] = {}
            for v in self.vehicles:
                cat = v.category
                categories.setdefault(cat, []).append(v)

            total_steps = len(self.vehicles) + len(categories)
            step = 0

            # 3. Verwerk per categorie
            for cat, vehicles in categories.items():
                cat_dir = self.output_dir / cat
                stream_dir = cat_dir / "stream"
                meta_dir = cat_dir / "meta"

                if not self.dry_run:
                    stream_dir.mkdir(parents=True, exist_ok=True)
                    meta_dir.mkdir(parents=True, exist_ok=True)

                stats["categories"][cat] = len(vehicles)
                if cat == "_unknown":
                    stats["unknown"] += len(vehicles)

                # Kopieer bestanden per voertuig
                for v in vehicles:
                    self.progress.emit(
                        int((step / total_steps) * 100),
                        f"Verwerken: {v.name}"
                    )
                    step += 1

                    # Stream bestanden
                    for sf in v.stream_files:
                        dest = stream_dir / sf.name
                        if not self.dry_run:
                            try:
                                shutil.copy2(sf, dest)
                            except Exception as e:
                                stats["errors"].append(f"{v.name}: {e}")

                    # Meta bestanden (prefix met voertuignaam)
                    for mf in v.meta_files:
                        # Voeg voertuignaam prefix toe als die er nog niet in zit
                        new_name = mf.name
                        if not new_name.lower().startswith(v.name):
                            new_name = f"{v.name}_{mf.name}"
                        dest = meta_dir / new_name
                        if not self.dry_run:
                            try:
                                shutil.copy2(mf, dest)
                            except Exception as e:
                                stats["errors"].append(f"{v.name}: {e}")

                    stats["processed"] += 1

                # Genereer fxmanifest.lua
                manifest_content = generate_fxmanifest(cat, vehicles)
                if not self.dry_run:
                    manifest_path = cat_dir / "fxmanifest.lua"
                    manifest_path.write_text(manifest_content, encoding="utf-8")

                self.progress.emit(int((step / total_steps) * 100), f"fxmanifest.lua voor {cat}")
                step += 1

            self.progress.emit(100, "Klaar!")
            self.finished.emit(stats)

        except Exception as e:
            self.error.emit(str(e))

    def _make_backup(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.source_dir.parent / f"backup_{self.source_dir.name}_{timestamp}.zip"
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in self.source_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(self.source_dir.parent))
        return backup_path


# ─────────────────────────────────────────────────────────────────────────────
#  DROP ZONE WIDGET
# ─────────────────────────────────────────────────────────────────────────────

class DropZone(QLabel):
    folder_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(120)
        self._set_idle()

    def _set_idle(self):
        self.setText(
            "📂  Sleep hier je resources folder naartoe\n"
            "of klik om te bladeren"
        )
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['surface']};
                border: 2px dashed {COLORS['border']};
                border-radius: 12px;
                color: {COLORS['text_dim']};
                font-size: 14px;
                padding: 20px;
            }}
        """)

    def _set_active(self):
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['surface2']};
                border: 2px dashed {COLORS['accent']};
                border-radius: 12px;
                color: {COLORS['accent']};
                font-size: 14px;
                padding: 20px;
            }}
        """)

    def _set_loaded(self, path: str):
        self.setText(f"✅  {path}")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['success']};
                border-radius: 12px;
                color: {COLORS['success']};
                font-size: 13px;
                padding: 20px;
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_active()

    def dragLeaveEvent(self, event):
        self._set_idle()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self._set_loaded(path)
                self.folder_dropped.emit(path)
            else:
                self._set_idle()

    def mousePressEvent(self, event):
        path = QFileDialog.getExistingDirectory(self, "Selecteer resources folder")
        if path:
            self._set_loaded(path)
            self.folder_dropped.emit(path)


# ─────────────────────────────────────────────────────────────────────────────
#  OVERRIDE DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class OverrideDialog(QDialog):
    """Dialog om handmatig categorieën toe te wijzen aan voertuigen."""

    def __init__(self, vehicles: list[VehicleInfo], parent=None):
        super().__init__(parent)
        self.vehicles = vehicles
        self.setWindowTitle("Handmatige Categorie Override")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("🔧 Handmatige Categorie Toewijzing")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['accent']};")
        layout.addWidget(title)

        info = QLabel("Pas hier de categorie aan voor voertuigen die incorrect of onbekend zijn gedetecteerd.")
        info.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 12px;")
        layout.addWidget(info)

        # Filter checkboxes
        filter_layout = QHBoxLayout()
        self.show_unknown_only = QCheckBox("Toon alleen _unknown voertuigen")
        self.show_unknown_only.setChecked(True)
        self.show_unknown_only.stateChanged.connect(self._refresh_table)
        filter_layout.addWidget(self.show_unknown_only)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Voertuig", "Originele Map", "Gedetecteerd", "Toegewezen", "Problemen"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 160)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Bulk acties
        bulk_layout = QHBoxLayout()
        bulk_label = QLabel("Bulk toewijzing voor geselecteerde rijen:")
        bulk_label.setStyleSheet(f"color: {COLORS['text_dim']};")
        self.bulk_combo = QComboBox()
        self.bulk_combo.addItems(ALL_CATEGORIES)
        bulk_btn = QPushButton("Toewijzen")
        bulk_btn.clicked.connect(self._bulk_assign)
        bulk_layout.addWidget(bulk_label)
        bulk_layout.addWidget(self.bulk_combo)
        bulk_layout.addWidget(bulk_btn)
        bulk_layout.addStretch()
        layout.addLayout(bulk_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._refresh_table()

    def _refresh_table(self):
        only_unknown = self.show_unknown_only.isChecked()
        filtered = [v for v in self.vehicles if (not only_unknown or v.is_unknown)]

        self.table.setRowCount(len(filtered))
        self._filtered_vehicles = filtered

        for row, v in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(v.name))
            self.table.setItem(row, 1, QTableWidgetItem(v.original_name))

            detected = v.detected_category or "—"
            det_item = QTableWidgetItem(detected)
            if detected == "_unknown" or detected == "—":
                det_item.setForeground(QColor(COLORS["warning"]))
            else:
                det_item.setForeground(QColor(COLORS["success"]))
            self.table.setItem(row, 2, det_item)

            # Dropdown voor toewijzing
            combo = QComboBox()
            combo.addItems(ALL_CATEGORIES)
            current = v.assigned_category or v.detected_category or "_unknown"
            idx = combo.findText(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.setProperty("vehicle_index", self.vehicles.index(v))
            self.table.setCellWidget(row, 3, combo)

            issues_text = " | ".join(v.issues) if v.issues else "✓"
            issue_item = QTableWidgetItem(issues_text)
            issue_item.setForeground(QColor(COLORS["warning"] if v.issues else COLORS["success"]))
            self.table.setItem(row, 4, issue_item)

    def _bulk_assign(self):
        cat = self.bulk_combo.currentText()
        for row in self.table.selectedItems():
            r = row.row()
            combo = self.table.cellWidget(r, 3)
            if combo:
                idx = combo.findText(cat)
                if idx >= 0:
                    combo.setCurrentIndex(idx)

    def _save_and_accept(self):
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 3)
            if combo:
                v_idx = combo.property("vehicle_index")
                self.vehicles[v_idx].assigned_category = combo.currentText()
        self.accept()


# ─────────────────────────────────────────────────────────────────────────────
#  PREVIEW PANEL
# ─────────────────────────────────────────────────────────────────────────────

class PreviewPanel(QWidget):
    """Toont een live boomstructuur van de nieuwe organisatie."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📁 Preview — Nieuwe Structuur")
        header.setStyleSheet(f"font-weight: bold; color: {COLORS['accent']}; font-size: 13px;")
        layout.addWidget(header)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree)

    def update_preview(self, vehicles: list[VehicleInfo], output_dir: str):
        self.tree.clear()

        root_item = QTreeWidgetItem([f"📁 {output_dir or '[output folder]'}"])
        root_item.setForeground(0, QColor(COLORS["accent"]))
        self.tree.addTopLevelItem(root_item)

        # Groepeer per categorie
        categories: dict[str, list[VehicleInfo]] = {}
        for v in vehicles:
            categories.setdefault(v.category, []).append(v)

        for cat in sorted(categories.keys()):
            vlist = categories[cat]
            color = COLORS["warning"] if cat == "_unknown" else COLORS["success"]

            cat_item = QTreeWidgetItem([f"📁 {cat}  ({len(vlist)} voertuig{'en' if len(vlist) != 1 else ''})"])
            cat_item.setForeground(0, QColor(color))
            root_item.addChild(cat_item)

            stream_item = QTreeWidgetItem(["📁 stream/"])
            stream_item.setForeground(0, QColor(COLORS["text_dim"]))
            cat_item.addChild(stream_item)

            meta_item = QTreeWidgetItem(["📁 meta/"])
            meta_item.setForeground(0, QColor(COLORS["text_dim"]))
            cat_item.addChild(meta_item)

            manifest_item = QTreeWidgetItem(["📄 fxmanifest.lua"])
            manifest_item.setForeground(0, QColor(COLORS["accent2"]))
            cat_item.addChild(manifest_item)

            # Toon eerste paar voertuigen
            for v in vlist[:5]:
                v_item = QTreeWidgetItem([f"  🚗 {v.name}"])
                v_item.setForeground(0, QColor(COLORS["text"]))
                # Stream bestanden
                for sf in v.stream_files[:3]:
                    sf_item = QTreeWidgetItem([f"    └ {sf.name}"])
                    sf_item.setForeground(0, QColor(COLORS["text_dim"]))
                    stream_item.addChild(sf_item)
                # Meta bestanden
                for mf in v.meta_files[:3]:
                    mf_item = QTreeWidgetItem([f"    └ {v.name}_{mf.name}"])
                    mf_item.setForeground(0, QColor(COLORS["text_dim"]))
                    meta_item.addChild(mf_item)

            if len(vlist) > 5:
                more_item = QTreeWidgetItem([f"  ... en {len(vlist) - 5} meer"])
                more_item.setForeground(0, QColor(COLORS["text_dim"]))
                cat_item.addChild(more_item)

        root_item.setExpanded(True)
        for i in range(root_item.childCount()):
            root_item.child(i).setExpanded(True)


# ─────────────────────────────────────────────────────────────────────────────
#  HOOFD VENSTER
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"FiveM Asset Organizer  v{VERSION}")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STYLESHEET)

        self.vehicles: list[VehicleInfo] = []
        self.source_dir: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        self.worker: Optional[OrganizerWorker] = None

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("⚡ FiveM Asset Organizer")
        title.setObjectName("title")
        subtitle = QLabel(f"v{VERSION}  •  Voertuig resource reorganisatie tool")
        subtitle.setObjectName("subtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(sep)

        # Splitter: links configuratie, rechts preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ── LINKER PANEEL ──
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(12)

        # Input
        input_group = QGroupBox("1. Input — Resources Folder")
        input_layout = QVBoxLayout(input_group)
        self.drop_zone = DropZone()
        self.drop_zone.folder_dropped.connect(self._on_input_selected)
        input_layout.addWidget(self.drop_zone)
        left_layout.addWidget(input_group)

        # Output
        output_group = QGroupBox("2. Output — Doelmap")
        output_layout = QHBoxLayout(output_group)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Selecteer output folder...")
        self.output_edit.textChanged.connect(self._on_output_changed)
        browse_btn = QPushButton("📂 Bladeren")
        browse_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(browse_btn)
        left_layout.addWidget(output_group)

        # Opties
        options_group = QGroupBox("3. Opties")
        options_layout = QVBoxLayout(options_group)
        self.dry_run_check = QCheckBox("🔍 Dry-run modus (geen bestanden aanpassen)")
        self.dry_run_check.setChecked(True)
        self.backup_check = QCheckBox("💾 Backup maken voor het beginnen")
        self.backup_check.setChecked(True)
        options_layout.addWidget(self.dry_run_check)
        options_layout.addWidget(self.backup_check)
        left_layout.addWidget(options_group)

        # Status & statistieken
        stats_group = QGroupBox("4. Scan Resultaten")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_label = QLabel("Nog geen scan uitgevoerd.")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_dim']};")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        stats_btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("🔍 Scannen")
        self.scan_btn.setObjectName("primary")
        self.scan_btn.clicked.connect(self._do_scan)
        self.scan_btn.setEnabled(False)

        self.override_btn = QPushButton("🔧 Categorieën Aanpassen")
        self.override_btn.clicked.connect(self._open_override)
        self.override_btn.setEnabled(False)

        stats_btn_layout.addWidget(self.scan_btn)
        stats_btn_layout.addWidget(self.override_btn)
        stats_layout.addLayout(stats_btn_layout)
        left_layout.addWidget(stats_group)

        # Voortgang
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.progress_label)

        # Actie knoppen
        action_layout = QHBoxLayout()
        self.dryrun_run_btn = QPushButton("▶ Dry-run Preview")
        self.dryrun_run_btn.setObjectName("primary")
        self.dryrun_run_btn.clicked.connect(lambda: self._do_organize(dry_run=True))
        self.dryrun_run_btn.setEnabled(False)

        self.organize_btn = QPushButton("✅ Organiseren!")
        self.organize_btn.setObjectName("success")
        self.organize_btn.clicked.connect(lambda: self._do_organize(dry_run=False))
        self.organize_btn.setEnabled(False)

        action_layout.addWidget(self.dryrun_run_btn)
        action_layout.addWidget(self.organize_btn)
        left_layout.addLayout(action_layout)

        left_layout.addStretch()

        # ── RECHTER PANEEL ──
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 0, 0, 0)

        self.tabs = QTabWidget()

        # Preview tab
        self.preview_panel = PreviewPanel()
        self.tabs.addTab(self.preview_panel, "📁 Structuur Preview")

        # Log tab
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText("Log berichten verschijnen hier...")
        self.tabs.addTab(self.log_edit, "📋 Log")

        # Issues tab
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(3)
        self.issues_table.setHorizontalHeaderLabels(["Voertuig", "Categorie", "Probleem"])
        self.issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.issues_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.issues_table.setAlternatingRowColors(True)
        self.tabs.addTab(self.issues_table, "⚠ Problemen (0)")

        right_layout.addWidget(self.tabs)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([420, 760])

    # ── EVENT HANDLERS ──

    def _on_input_selected(self, path: str):
        self.source_dir = Path(path)
        self.scan_btn.setEnabled(True)
        self._log(f"Input folder geselecteerd: {path}")

    def _on_output_changed(self, text: str):
        if text:
            self.output_dir = Path(text)
        self._update_action_buttons()

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Selecteer output folder")
        if path:
            self.output_edit.setText(path)
            self.output_dir = Path(path)

    def _do_scan(self):
        if not self.source_dir:
            return

        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self._log(f"\n{'='*50}")
        self._log(f"Scannen: {self.source_dir}")

        scanner = VehicleScanner(self.source_dir)

        def progress(pct, name):
            self.progress_bar.setValue(pct)
            self.progress_label.setText(f"Scannen: {name}")

        # Voer scan uit (sync voor simpliciciteit; bij >1000 bestanden eventueel async)
        self.vehicles = scanner.scan(progress_callback=progress)

        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")

        # Stats
        unknown = sum(1 for v in self.vehicles if v.is_unknown)
        issues = sum(1 for v in self.vehicles if v.has_issues)
        cats = set(v.category for v in self.vehicles)

        self.stats_label.setText(
            f"<b style='color:{COLORS['success']}'>{len(self.vehicles)}</b> voertuigen gevonden  •  "
            f"<b style='color:{COLORS['warning']}'>{unknown}</b> onbekend  •  "
            f"<b style='color:{COLORS['error']}'>{issues}</b> met problemen  •  "
            f"<b style='color:{COLORS['accent']}'>{len(cats)}</b> categorieën"
        )

        self._log(f"Scan klaar: {len(self.vehicles)} voertuigen")
        self._log(f"  Onbekend: {unknown}")
        self._log(f"  Met problemen: {issues}")
        if scanner.errors:
            for e in scanner.errors:
                self._log(f"  ❌ Fout: {e}", error=True)

        self._update_issues_tab()
        self._update_preview()

        self.scan_btn.setEnabled(True)
        self.override_btn.setEnabled(len(self.vehicles) > 0)
        self._update_action_buttons()

    def _open_override(self):
        dialog = OverrideDialog(self.vehicles, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._log("Handmatige categorieën opgeslagen.")
            self._update_preview()
            self._update_issues_tab()

    def _do_organize(self, dry_run: bool):
        if not self.vehicles or not self.output_dir:
            QMessageBox.warning(self, "Ontbrekende informatie", "Zorg dat je een input folder hebt gescand en een output folder hebt geselecteerd.")
            return

        # Bevestiging als niet dry-run
        if not dry_run:
            unknown_count = sum(1 for v in self.vehicles if v.is_unknown)
            msg = f"Je staat op het punt {len(self.vehicles)} voertuigen te organiseren naar:\n{self.output_dir}\n\n"
            if unknown_count:
                msg += f"⚠ {unknown_count} voertuigen worden in '_unknown' geplaatst.\n\n"
            if self.backup_check.isChecked():
                msg += "✅ Er wordt eerst een backup gemaakt.\n\n"
            msg += "Doorgaan?"
            reply = QMessageBox.question(self, "Bevestigen", msg)
            if reply != QMessageBox.StandardButton.Yes:
                return

        effective_dry_run = dry_run or self.dry_run_check.isChecked()
        make_backup = self.backup_check.isChecked() and not effective_dry_run

        self.organize_btn.setEnabled(False)
        self.dryrun_run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.worker = OrganizerWorker(
            vehicles=self.vehicles,
            output_dir=self.output_dir,
            dry_run=effective_dry_run,
            make_backup=make_backup,
            source_dir=self.source_dir,
        )
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished.connect(lambda s: self._on_worker_finished(s, effective_dry_run))
        self.worker.error.connect(self._on_worker_error)
        self.worker.start()

    def _on_worker_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.progress_label.setText(msg)

    def _on_worker_finished(self, stats: dict, was_dry_run: bool):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self._update_action_buttons()

        mode = "DRY-RUN" if was_dry_run else "DEFINITIEF"
        self._log(f"\n{'='*50}")
        self._log(f"✅ Organiseren klaar [{mode}]")
        self._log(f"  Verwerkt: {stats['processed']}/{stats['total']}")
        self._log(f"  Onbekend: {stats['unknown']}")
        if stats.get("backup_path"):
            self._log(f"  Backup: {stats['backup_path']}")
        for cat, count in sorted(stats["categories"].items()):
            self._log(f"  📁 {cat}: {count} voertuigen")
        if stats["errors"]:
            for e in stats["errors"]:
                self._log(f"  ❌ {e}", error=True)

        self.tabs.setCurrentIndex(1)  # Ga naar log tab

        if not was_dry_run:
            QMessageBox.information(
                self, "Klaar!",
                f"✅ {stats['processed']} voertuigen succesvol georganiseerd!\n\n"
                f"Output: {self.output_dir}\n"
                + (f"Backup: {stats['backup_path']}" if stats.get('backup_path') else "")
            )

    def _on_worker_error(self, msg: str):
        self.progress_bar.setVisible(False)
        self._log(f"❌ FOUT: {msg}", error=True)
        self._update_action_buttons()
        QMessageBox.critical(self, "Fout", f"Er is een fout opgetreden:\n{msg}")

    def _update_preview(self):
        self.preview_panel.update_preview(
            self.vehicles,
            str(self.output_dir) if self.output_dir else ""
        )

    def _update_issues_tab(self):
        issues = [(v, issue) for v in self.vehicles for issue in v.issues]
        self.issues_table.setRowCount(len(issues))
        for row, (v, issue) in enumerate(issues):
            self.issues_table.setItem(row, 0, QTableWidgetItem(v.name))
            cat_item = QTableWidgetItem(v.category)
            cat_item.setForeground(QColor(COLORS["warning"] if v.is_unknown else COLORS["success"]))
            self.issues_table.setItem(row, 1, cat_item)
            self.issues_table.setItem(row, 2, QTableWidgetItem(issue))
        self.tabs.setTabText(2, f"⚠ Problemen ({len(issues)})")

    def _update_action_buttons(self):
        ready = len(self.vehicles) > 0 and self.output_dir is not None
        self.dryrun_run_btn.setEnabled(ready)
        self.organize_btn.setEnabled(ready)

    def _log(self, msg: str, error: bool = False):
        color = COLORS["error"] if error else COLORS["text"]
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_edit.append(f'<span style="color:{COLORS["text_dim"]}">[{timestamp}]</span> <span style="color:{color}">{msg}</span>')


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FiveM Asset Organizer")
    app.setStyle("Fusion")

    # Donker palet voor Fusion stijl
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS["bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS["surface"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS["surface2"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS["surface2"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()