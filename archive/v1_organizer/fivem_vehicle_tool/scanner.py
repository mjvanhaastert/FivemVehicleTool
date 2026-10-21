"""Resource scanning and vehicle metadata detection."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from .constants import (
    MANIFEST_FILES,
    META_EXTENSIONS,
    STREAM_EXTENSIONS,
    VEHICLE_CLASS_MAP,
)
from .models import VehicleInfo


class VehicleScanner:
    """Scans a root folder recursively for FiveM vehicle resources."""

    def __init__(self, root: Path):
        self.root = root
        self.vehicles: list[VehicleInfo] = []
        self.errors: list[str] = []

    def scan(self, progress_callback=None) -> list[VehicleInfo]:
        self.vehicles = []
        self.errors = []

        resource_dirs = self._find_resource_dirs(self.root)
        total = len(resource_dirs)
        for i, resource_dir in enumerate(resource_dirs):
            if progress_callback:
                progress_callback(int((i / max(total, 1)) * 100), resource_dir.name)
            vehicle = self._parse_resource(resource_dir)
            if vehicle:
                self.vehicles.append(vehicle)

        return self.vehicles

    def _find_resource_dirs(self, root: Path) -> list[Path]:
        result: list[Path] = []
        try:
            for item in root.rglob("*"):
                if item.is_file() and item.name.lower() in MANIFEST_FILES:
                    result.append(item.parent)
        except PermissionError as exc:
            self.errors.append(str(exc))

        seen = set()
        unique = []
        for path in result:
            if path not in seen:
                seen.add(path)
                unique.append(path)
        return unique

    def _parse_resource(self, resource_dir: Path) -> VehicleInfo:
        name = self._normalize_name(resource_dir.name)
        vehicle = VehicleInfo(name=name, source_dir=resource_dir, original_name=resource_dir.name)

        for item in resource_dir.rglob("*"):
            if not item.is_file():
                continue
            ext = item.suffix.lower()
            filename = item.name.lower()
            if filename in MANIFEST_FILES:
                vehicle.manifest_files.append(item)
            elif ext in STREAM_EXTENSIONS:
                vehicle.stream_files.append(item)
            elif ext in META_EXTENSIONS:
                vehicle.meta_files.append(item)

        self._detect_category(vehicle)
        self._validate(vehicle)
        return vehicle

    def _detect_category(self, vehicle: VehicleInfo) -> None:
        for meta_file in vehicle.meta_files:
            if "vehicles" not in meta_file.name.lower() or meta_file.suffix.lower() != ".meta":
                continue
            try:
                root = ET.parse(meta_file).getroot()
            except Exception:
                continue

            for elem in root.iter("vehicleClass"):
                text = elem.text.strip() if elem.text else ""
                if text.startswith("VC_"):
                    vehicle.detected_category = self._vc_to_category(text[3:].lower())
                    vehicle.vehicle_class_raw = text
                    return
                if text.isdigit():
                    vehicle.detected_category = VEHICLE_CLASS_MAP.get(text, "_unknown")
                    vehicle.vehicle_class_raw = text
                    return

    @staticmethod
    def _vc_to_category(vc_name: str) -> str:
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
        return mapping.get(vc_name, "_unknown")

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.lower()
        normalized = re.sub(r"[\s\-]+", "_", normalized)
        normalized = re.sub(r"[^a-z0-9_]", "", normalized)
        normalized = re.sub(r"_+", "_", normalized).strip("_")
        return normalized or "vehicle"

    @staticmethod
    def _validate(vehicle: VehicleInfo) -> None:
        if not vehicle.stream_files:
            vehicle.issues.append("Geen stream bestanden gevonden (.yft/.ytd)")
        if not vehicle.meta_files:
            vehicle.issues.append("Geen meta bestanden gevonden")
        if not any("vehicles" in file.name.lower() for file in vehicle.meta_files):
            vehicle.issues.append("Geen vehicles.meta gevonden")
        if not any("handling" in file.name.lower() for file in vehicle.meta_files):
            vehicle.issues.append("Geen handling.meta gevonden")
        if vehicle.original_name != vehicle.name:
            vehicle.issues.append(f"Naam genormaliseerd: '{vehicle.original_name}' -> '{vehicle.name}'")
