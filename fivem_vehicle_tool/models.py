"""Shared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class VehicleInfo:
    """Represents one detected vehicle resource."""

    name: str
    source_dir: Path
    original_name: str = ""
    stream_files: list[Path] = field(default_factory=list)
    meta_files: list[Path] = field(default_factory=list)
    manifest_files: list[Path] = field(default_factory=list)
    detected_category: Optional[str] = None
    assigned_category: Optional[str] = None
    issues: list[str] = field(default_factory=list)
    vehicle_class_raw: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.original_name:
            self.original_name = self.name

    @property
    def category(self) -> str:
        return self.assigned_category or self.detected_category or "_unknown"

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def is_unknown(self) -> bool:
        return self.category == "_unknown"
