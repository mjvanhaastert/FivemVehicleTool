"""Application constants."""

from __future__ import annotations

VERSION = "1.1.0"

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

ALL_CATEGORIES = sorted(set(VEHICLE_CLASS_MAP.values())) + ["_unknown"]

STREAM_EXTENSIONS = {".yft", ".ytd", ".ycd", ".ymap", ".ytyp", ".ydd", ".yld", ".yvr"}
META_EXTENSIONS = {".meta", ".xml"}
MANIFEST_FILES = {"fxmanifest.lua", "__resource.lua"}

VEHICLES_ROOT_NAME = "Vehicles"

COLORS = {
    "bg": "#0f1117",
    "surface": "#1a1d27",
    "surface2": "#22263a",
    "border": "#2d3250",
    "accent": "#5b8af5",
    "accent2": "#7c5bf5",
    "success": "#3ecf8e",
    "warning": "#f5a623",
    "error": "#f55b5b",
    "text": "#e8eaf6",
    "text_dim": "#7b82a8",
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
    margin-top: 10px;
    padding: 8px;
    font-weight: bold;
    color: {COLORS['accent']};
}}
QPushButton {{
    background-color: {COLORS['surface2']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
}}
QPushButton#primary {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
}}
QPushButton#success {{
    background-color: {COLORS['success']};
    color: #0f1117;
    border: none;
}}
QLineEdit, QTextEdit, QTreeWidget, QTableWidget {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    color: {COLORS['text']};
}}
QProgressBar {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {COLORS['accent']};
}}
"""
