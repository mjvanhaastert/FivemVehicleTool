"""Worker that writes organized output to disk."""

from __future__ import annotations

import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from .constants import VEHICLES_ROOT_NAME
from .manifest import generate_combined_fxmanifest, meta_target_filename
from .models import VehicleInfo


class OrganizerWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(
        self,
        vehicles: list[VehicleInfo],
        output_dir: Path,
        dry_run: bool,
        make_backup: bool,
        source_dir: Path,
    ):
        super().__init__()
        self.vehicles = vehicles
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.make_backup = make_backup
        self.source_dir = source_dir

    def run(self) -> None:
        try:
            vehicles_root = self.output_dir / VEHICLES_ROOT_NAME
            stats = {
                "total": len(self.vehicles),
                "processed": 0,
                "unknown": 0,
                "errors": [],
                "backup_path": None,
                "categories": {},
                "vehicles_root": str(vehicles_root),
            }

            if self.make_backup and not self.dry_run:
                self.progress.emit(0, "Backup maken...")
                backup_path = self._make_backup()
                stats["backup_path"] = str(backup_path)

            categories: dict[str, list[VehicleInfo]] = {}
            for vehicle in self.vehicles:
                categories.setdefault(vehicle.category, []).append(vehicle)

            total_steps = len(self.vehicles) + 1
            step = 0

            for category, vehicles in categories.items():
                category_dir = vehicles_root / category
                stream_dir = category_dir / "stream"
                meta_dir = category_dir / "meta"

                if not self.dry_run:
                    stream_dir.mkdir(parents=True, exist_ok=True)
                    meta_dir.mkdir(parents=True, exist_ok=True)

                stats["categories"][category] = len(vehicles)
                if category == "_unknown":
                    stats["unknown"] += len(vehicles)

                for vehicle in vehicles:
                    self.progress.emit(int((step / max(total_steps, 1)) * 100), f"Verwerken: {vehicle.name}")
                    step += 1

                    for stream_file in vehicle.stream_files:
                        target_name = self._safe_stream_filename(stream_dir, vehicle.name, stream_file.name)
                        target = stream_dir / target_name
                        if not self.dry_run:
                            self._copy_file(stream_file, target, stats, vehicle.name)

                    for meta_file in vehicle.meta_files:
                        target_name = meta_target_filename(vehicle, meta_file.name)
                        target = meta_dir / target_name
                        if not self.dry_run:
                            self._copy_file(meta_file, target, stats, vehicle.name)

                    stats["processed"] += 1

            manifest_content = generate_combined_fxmanifest(categories)
            if not self.dry_run:
                vehicles_root.mkdir(parents=True, exist_ok=True)
                manifest_path = vehicles_root / "fxmanifest.lua"
                manifest_path.write_text(manifest_content, encoding="utf-8")

            self.progress.emit(int((step / max(total_steps, 1)) * 100), "fxmanifest.lua genereren")
            self.progress.emit(100, "Klaar!")
            self.finished.emit(stats)

        except Exception as exc:
            self.error.emit(str(exc))

    @staticmethod
    def _copy_file(source: Path, destination: Path, stats: dict, vehicle_name: str) -> None:
        try:
            shutil.copy2(source, destination)
        except Exception as exc:
            stats["errors"].append(f"{vehicle_name}: {exc}")

    @staticmethod
    def _safe_stream_filename(stream_dir: Path, vehicle_name: str, original_name: str) -> str:
        candidate = stream_dir / original_name
        if not candidate.exists():
            return original_name

        prefixed = f"{vehicle_name}_{original_name}"
        candidate = stream_dir / prefixed
        if not candidate.exists():
            return prefixed

        stem = Path(original_name).stem
        suffix = Path(original_name).suffix
        index = 1
        while True:
            candidate_name = f"{vehicle_name}_{stem}_{index}{suffix}"
            if not (stream_dir / candidate_name).exists():
                return candidate_name
            index += 1

    def _make_backup(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.source_dir.parent / f"backup_{self.source_dir.name}_{timestamp}.zip"
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for item in self.source_dir.rglob("*"):
                if item.is_file():
                    archive.write(item, item.relative_to(self.source_dir.parent))
        return backup_path
