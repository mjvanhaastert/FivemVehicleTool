"""fxmanifest generation helpers."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Optional

from .models import VehicleInfo


def meta_target_filename(vehicle: VehicleInfo, original_name: str) -> str:
    """Prefix meta names with vehicle name to avoid collisions."""
    if original_name.lower().startswith(vehicle.name.lower()):
        return original_name
    return f"{vehicle.name}_{original_name}"


def detect_meta_type(filename: str) -> Optional[str]:
    fn = filename.lower()
    if "vehicles" in fn:
        return "VEHICLE_METADATA_FILE"
    if "handling" in fn:
        return "HANDLING_FILE"
    if "carcols" in fn:
        return "CARCOLS_FILE"
    if "carvariations" in fn:
        return "VEHICLE_VARIATION_FILE"
    if "vehiclelayouts" in fn:
        return "VEHICLE_LAYOUTS_FILE"
    if "contentunlocks" in fn:
        return "CONTENT_UNLOCKING_META_FILE"
    return None


def generate_combined_fxmanifest(categories: dict[str, list[VehicleInfo]]) -> str:
    """Generate one manifest for the complete Vehicles resource."""
    data_groups: dict[str, list[str]] = defaultdict(list)

    for category, vehicles in categories.items():
        for vehicle in vehicles:
            for meta_file in vehicle.meta_files:
                meta_type = detect_meta_type(meta_file.name)
                if not meta_type:
                    continue
                target_name = meta_target_filename(vehicle, meta_file.name)
                rel_path = Path(category) / "meta" / target_name
                data_groups[meta_type].append(str(rel_path).replace("\\", "/"))

    lines = [
        "fx_version 'cerulean'",
        "game 'gta5'",
        "",
        "name 'vehicles_unified'",
        "description 'Unified FiveM vehicle pack organized by category'",
        "version '1.0.0'",
        "",
        "files {",
        "    '**/stream/**',",
        "    '**/meta/*.meta',",
        "    '**/meta/*.xml'",
        "}",
        "",
    ]

    for meta_type in sorted(data_groups.keys()):
        lines.append(f"-- {meta_type}")
        lines.append(f"data_file '{meta_type}' {{")
        for rel in sorted(set(data_groups[meta_type])):
            lines.append(f"    '{rel}',")
        lines.append("}")
        lines.append("")

    return "\n".join(lines)
