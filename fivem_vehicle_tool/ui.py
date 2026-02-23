"""PyQt UI for the FiveM vehicle organizer."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .constants import ALL_CATEGORIES, COLORS, STYLESHEET, VERSION, VEHICLES_ROOT_NAME
from .models import VehicleInfo
from .organizer import OrganizerWorker
from .scanner import VehicleScanner


class OverrideDialog(QDialog):
    """Dialog for manually overriding vehicle categories."""

    def __init__(self, vehicles: list[VehicleInfo], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.vehicles = vehicles
        self.setWindowTitle("Categorieen aanpassen")
        self.setMinimumSize(800, 500)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Voertuig", "Originele map", "Gedetecteerd", "Toegewezen"])
        self.table.setRowCount(len(self.vehicles))

        for row, vehicle in enumerate(self.vehicles):
            self.table.setItem(row, 0, QTableWidgetItem(vehicle.name))
            self.table.setItem(row, 1, QTableWidgetItem(vehicle.original_name))
            self.table.setItem(row, 2, QTableWidgetItem(vehicle.detected_category or "_unknown"))

            combo = QComboBox()
            combo.addItems(ALL_CATEGORIES)
            current = vehicle.assigned_category or vehicle.detected_category or "_unknown"
            combo.setCurrentText(current)
            combo.setProperty("vehicle_index", row)
            self.table.setCellWidget(row, 3, combo)

        layout.addWidget(self.table)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save_and_accept(self) -> None:
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 3)
            if combo:
                vehicle_idx = combo.property("vehicle_index")
                self.vehicles[vehicle_idx].assigned_category = combo.currentText()
        self.accept()


class PreviewPanel(QWidget):
    """Preview tree for resulting folder structure."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Preview structuur")
        label.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold;")
        layout.addWidget(label)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout.addWidget(self.tree)

    def update_preview(self, vehicles: list[VehicleInfo], output_dir: str) -> None:
        self.tree.clear()
        root_display = str(Path(output_dir) / VEHICLES_ROOT_NAME) if output_dir else f"[output]/{VEHICLES_ROOT_NAME}"
        root = QTreeWidgetItem([f"{root_display}/"])
        root.setForeground(0, QColor(COLORS["accent"]))
        self.tree.addTopLevelItem(root)

        categories: dict[str, list[VehicleInfo]] = {}
        for vehicle in vehicles:
            categories.setdefault(vehicle.category, []).append(vehicle)

        for category in sorted(categories.keys()):
            cat_item = QTreeWidgetItem([f"{category}/ ({len(categories[category])} voertuigen)"])
            root.addChild(cat_item)
            cat_item.addChild(QTreeWidgetItem(["stream/"]))
            cat_item.addChild(QTreeWidgetItem(["meta/"]))

        root.addChild(QTreeWidgetItem(["fxmanifest.lua"]))
        root.setExpanded(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"FiveM Vehicle Tool v{VERSION}")
        self.setMinimumSize(1100, 760)
        self.setStyleSheet(STYLESHEET)

        self.vehicles: list[VehicleInfo] = []
        self.source_dir: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        self.worker: Optional[OrganizerWorker] = None

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        header = QLabel("FiveM Vehicle Tool")
        header.setStyleSheet(f"font-size: 22px; color: {COLORS['accent']}; font-weight: bold;")
        main_layout.addWidget(header)

        sub = QLabel("Standaard Python structuur + 1 gecombineerde Vehicles resource")
        sub.setStyleSheet(f"color: {COLORS['text_dim']};")
        main_layout.addWidget(sub)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {COLORS['border']};")
        main_layout.addWidget(line)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        splitter.addWidget(right)
        splitter.setSizes([460, 640])

        input_group = QGroupBox("Input folder")
        input_layout = QHBoxLayout(input_group)
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Folder met meerdere vehicle resources")
        input_btn = QPushButton("Bladeren")
        input_btn.clicked.connect(self._browse_input)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        left_layout.addWidget(input_group)

        output_group = QGroupBox("Output folder")
        output_layout = QHBoxLayout(output_group)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Hierin wordt Vehicles/ aangemaakt")
        self.output_edit.textChanged.connect(self._on_output_changed)
        output_btn = QPushButton("Bladeren")
        output_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        left_layout.addWidget(output_group)

        options_group = QGroupBox("Opties")
        options_layout = QVBoxLayout(options_group)
        self.dry_run_check = QCheckBox("Dry-run (geen bestanden schrijven)")
        self.dry_run_check.setChecked(True)
        self.backup_check = QCheckBox("Backup maken")
        self.backup_check.setChecked(True)
        options_layout.addWidget(self.dry_run_check)
        options_layout.addWidget(self.backup_check)
        left_layout.addWidget(options_group)

        actions = QHBoxLayout()
        self.scan_btn = QPushButton("Scannen")
        self.scan_btn.setObjectName("primary")
        self.scan_btn.clicked.connect(self._do_scan)

        self.override_btn = QPushButton("Categorieen aanpassen")
        self.override_btn.clicked.connect(self._open_override)
        self.override_btn.setEnabled(False)

        actions.addWidget(self.scan_btn)
        actions.addWidget(self.override_btn)
        left_layout.addLayout(actions)

        run_actions = QHBoxLayout()
        self.dryrun_btn = QPushButton("Dry-run preview")
        self.dryrun_btn.setObjectName("primary")
        self.dryrun_btn.clicked.connect(lambda: self._do_organize(force_dry_run=True))
        self.dryrun_btn.setEnabled(False)

        self.organize_btn = QPushButton("Organiseren")
        self.organize_btn.setObjectName("success")
        self.organize_btn.clicked.connect(lambda: self._do_organize(force_dry_run=False))
        self.organize_btn.setEnabled(False)

        run_actions.addWidget(self.dryrun_btn)
        run_actions.addWidget(self.organize_btn)
        left_layout.addLayout(run_actions)

        self.stats_label = QLabel("Nog geen scan uitgevoerd.")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_dim']};")
        left_layout.addWidget(self.stats_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {COLORS['text_dim']};")
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.progress_label)
        left_layout.addStretch()

        self.tabs = QTabWidget()
        self.preview = PreviewPanel()
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.tabs.addTab(self.preview, "Structuur")
        self.tabs.addTab(self.log_edit, "Log")
        right_layout.addWidget(self.tabs)

    def _browse_input(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Selecteer input folder")
        if not path:
            return
        self.input_edit.setText(path)
        self.source_dir = Path(path)
        self._log(f"Input geselecteerd: {path}")

    def _browse_output(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Selecteer output folder")
        if not path:
            return
        self.output_edit.setText(path)
        self.output_dir = Path(path)
        self._log(f"Output geselecteerd: {path}")
        self._update_action_buttons()

    def _on_output_changed(self, text: str) -> None:
        self.output_dir = Path(text) if text else None
        self._update_action_buttons()
        self._update_preview()

    def _do_scan(self) -> None:
        source_text = self.input_edit.text().strip()
        if not source_text:
            QMessageBox.warning(self, "Input ontbreekt", "Selecteer eerst een input folder.")
            return

        self.source_dir = Path(source_text)
        scanner = VehicleScanner(self.source_dir)

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self._log(f"Scannen gestart: {self.source_dir}")

        def on_progress(percent: int, name: str) -> None:
            self.progress_bar.setValue(percent)
            self.progress_label.setText(f"Scannen: {name}")

        self.vehicles = scanner.scan(progress_callback=on_progress)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")

        unknown = sum(1 for vehicle in self.vehicles if vehicle.is_unknown)
        issues = sum(1 for vehicle in self.vehicles if vehicle.has_issues)
        categories = len(set(vehicle.category for vehicle in self.vehicles))
        self.stats_label.setText(
            f"{len(self.vehicles)} voertuigen gevonden | {unknown} unknown | "
            f"{issues} met issues | {categories} categorieen"
        )

        self._log(f"Scan klaar: {len(self.vehicles)} voertuigen")
        self.override_btn.setEnabled(bool(self.vehicles))
        self._update_action_buttons()
        self._update_preview()

    def _open_override(self) -> None:
        if not self.vehicles:
            return
        dialog = OverrideDialog(self.vehicles, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._log("Handmatige categorieen opgeslagen.")
            self._update_preview()

    def _do_organize(self, force_dry_run: bool) -> None:
        if not self.vehicles or not self.output_dir or not self.source_dir:
            QMessageBox.warning(self, "Onvolledig", "Voer eerst scan uit en kies output folder.")
            return

        effective_dry_run = force_dry_run or self.dry_run_check.isChecked()
        make_backup = self.backup_check.isChecked() and not effective_dry_run

        if not effective_dry_run:
            target = self.output_dir / VEHICLES_ROOT_NAME
            answer = QMessageBox.question(
                self,
                "Bevestigen",
                f"Doorgaan met schrijven naar:\n{target}\n\nEr wordt 1 centrale fxmanifest.lua gemaakt.",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.organize_btn.setEnabled(False)
        self.dryrun_btn.setEnabled(False)

        self.worker = OrganizerWorker(
            vehicles=self.vehicles,
            output_dir=self.output_dir,
            dry_run=effective_dry_run,
            make_backup=make_backup,
            source_dir=self.source_dir,
        )
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished.connect(lambda stats: self._on_worker_finished(stats, effective_dry_run))
        self.worker.error.connect(self._on_worker_error)
        self.worker.start()

    def _on_worker_progress(self, percent: int, message: str) -> None:
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)

    def _on_worker_finished(self, stats: dict, was_dry_run: bool) -> None:
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self._update_action_buttons()

        mode = "DRY-RUN" if was_dry_run else "DEFINITIEF"
        self._log(f"Organiseren klaar [{mode}]")
        self._log(f"Verwerkt: {stats['processed']}/{stats['total']}")
        self._log(f"Vehicles root: {stats['vehicles_root']}")
        for category, count in sorted(stats["categories"].items()):
            self._log(f"- {category}: {count} voertuigen")
        if stats.get("backup_path"):
            self._log(f"Backup: {stats['backup_path']}")
        for err in stats.get("errors", []):
            self._log(f"Fout: {err}", error=True)

        if not was_dry_run:
            QMessageBox.information(
                self,
                "Klaar",
                f"{stats['processed']} voertuigen georganiseerd.\n\n"
                f"Pad: {stats['vehicles_root']}\n"
                "Manifest: Vehicles/fxmanifest.lua",
            )

    def _on_worker_error(self, message: str) -> None:
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self._update_action_buttons()
        self._log(f"FOUT: {message}", error=True)
        QMessageBox.critical(self, "Fout", message)

    def _update_preview(self) -> None:
        self.preview.update_preview(self.vehicles, str(self.output_dir) if self.output_dir else "")

    def _update_action_buttons(self) -> None:
        ready = bool(self.vehicles) and self.output_dir is not None
        self.dryrun_btn.setEnabled(ready)
        self.organize_btn.setEnabled(ready)

    def _log(self, message: str, error: bool = False) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = COLORS["error"] if error else COLORS["text"]
        self.log_edit.append(
            f'<span style="color:{COLORS["text_dim"]}">[{timestamp}]</span> '
            f'<span style="color:{color}">{message}</span>'
        )


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("FiveM Vehicle Tool")
    app.setStyle("Fusion")

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
