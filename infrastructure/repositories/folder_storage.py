"""Folder-based persistence for BPMN data stores.

This module materializes the BPMN data storages as filesystem folders:
RAW, CLEANED, PROCESSED/MDM, and REJECTED.
"""
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from domain.entities import Dataset, RejectionLog
from domain.exceptions import RepositorioException


class FolderStorage:
    """Persists pipeline artifacts in folders that mirror BPMN states."""

    MASTER_FILE = "master_dataset.csv"
    METADATA_FILE = "master_metadata.json"

    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "RAW"
        self.cleaned_dir = self.base_dir / "CLEANED"
        self.mdm_dir = self.base_dir / "PROCESSED" / "MDM"
        self.rejected_dir = self.base_dir / "REJECTED"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        for directory in (
            self.raw_dir,
            self.cleaned_dir,
            self.mdm_dir,
            self.rejected_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def persist_raw(self, dataset: Dataset) -> Path:
        """Stores the extracted original dataset in RAW."""
        return self._write_json(self.raw_dir / f"{dataset.id}.json", dataset.to_dict())

    def persist_cleaned(self, dataset: Dataset) -> Path:
        """Stores the cleaned dataset in CLEANED."""
        return self._write_json(
            self.cleaned_dir / f"{dataset.id}.json",
            dataset.to_dict(),
        )

    def persist_rejection(self, rejection_log: RejectionLog) -> Path:
        """Stores rejection details with gateway and business rule context."""
        return self._write_json(
            self.rejected_dir / f"{rejection_log.dataset_id}_{rejection_log.id}.json",
            rejection_log.to_dict(),
        )

    def append_to_master(self, dataset: Dataset) -> Path:
        """Appends accepted records to the single MDM master table as CSV."""
        records = dataset.records if dataset.records else dataset.rows_preview
        csv_path = self.mdm_dir / self.MASTER_FILE
        meta_path = self.mdm_dir / self.METADATA_FILE

        metadata = self._read_metadata(meta_path)
        existing_keys = self._read_existing_keys(csv_path)
        new_records = []

        for row in records:
            normalized_row = {k.lower(): v for k, v in row.items()}
            key = self._record_key(normalized_row)
            if key in existing_keys:
                continue
            new_records.append(normalized_row)
            existing_keys.add(key)

        if not new_records:
            return csv_path

        fieldnames = self._get_fieldnames(new_records)
        file_exists = csv_path.exists()

        try:
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            with csv_path.open("a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
                if not file_exists:
                    writer.writeheader()
                writer.writerows(new_records)
        except OSError as exc:
            raise RepositorioException(
                "Failed to append to MDM master CSV",
                context={"path": str(csv_path), "error": str(exc)},
            )

        metadata["dataset_ids"] = sorted(set(metadata["dataset_ids"] + [dataset.id]))
        metadata["total_records"] = metadata["total_records"] + len(new_records)
        self._write_json(meta_path, metadata)

        return csv_path

    def _read_metadata(self, meta_path: Path) -> Dict[str, Any]:
        if not meta_path.exists():
            return {"table": "master_dataset", "dataset_ids": [], "total_records": 0}
        try:
            with meta_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {"table": "master_dataset", "dataset_ids": [], "total_records": 0}

    def _read_existing_keys(self, csv_path: Path) -> set:
        keys: set = set()
        if not csv_path.exists():
            return keys
        try:
            with csv_path.open("r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    keys.add(self._record_key(row))
        except (OSError, csv.Error):
            pass
        return keys

    @staticmethod
    def _get_fieldnames(records: List[Dict[str, Any]]) -> List[str]:
        standard = [
            "ubicacion", "tamano_m2", "habitaciones", "banos", "estrato", "precio",
            "parqueadero", "long_com_corr", "parques", "vias",
            "remocion_masa", "grandes_superficies", "colegios", "hospitales",
            "fecha", "precio_unitario", "puntaje_entorno", "densidad_comercial",
            "bano_por_hab", "parqueadero_ratio",
        ]
        present = {k for r in records for k in r.keys()}
        return [c for c in standard if c in present] + sorted(set().union(*(r.keys() for r in records)) - set(standard))

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> Path:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = path.with_suffix(path.suffix + ".tmp")
            with tmp_path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
            tmp_path.replace(path)
            return path
        except OSError as exc:
            raise RepositorioException(
                "Failed to persist pipeline artifact",
                context={"path": str(path), "error": str(exc)},
            )

    @staticmethod
    def _record_key(row: Dict[str, Any]) -> tuple[Any, ...]:
        return (
            str(row.get("ubicacion", "")),
            str(row.get("tamano_m2", "")),
            str(row.get("habitaciones", "")),
        )
