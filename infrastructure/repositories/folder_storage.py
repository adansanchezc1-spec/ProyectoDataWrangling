"""Folder-based persistence for BPMN data stores.

This module materializes the BPMN data storages as filesystem folders:
RAW, CLEANED, PROCESSED/MDM, and REJECTED.
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from domain.entities import Dataset, RejectionLog
from domain.exceptions import RepositorioException


class FolderStorage:
    """Persists pipeline artifacts in folders that mirror BPMN states."""

    MASTER_FILE = "master_dataset.json"

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
        """Appends accepted records to the single MDM master table."""
        master_path = self.mdm_dir / self.MASTER_FILE
        master = self._read_master(master_path)
        records = dataset.records if dataset.records else dataset.rows_preview
        existing_keys = {self._record_key(row) for row in master["records"]}

        for row in records:
            key = self._record_key(row)
            if key in existing_keys:
                continue
            master["records"].append(dict(row))
            existing_keys.add(key)

        master["total_records"] = len(master["records"])
        master["dataset_ids"] = sorted(set(master["dataset_ids"] + [dataset.id]))
        return self._write_json(master_path, master)

    def _read_master(self, master_path: Path) -> Dict[str, Any]:
        if not master_path.exists():
            return {
                "table": "master_dataset",
                "dataset_ids": [],
                "total_records": 0,
                "records": [],
            }
        try:
            with master_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            raise RepositorioException(
                "Failed to read MDM master dataset",
                context={"path": str(master_path), "error": str(exc)},
            )
        data.setdefault("table", "master_dataset")
        data.setdefault("dataset_ids", [])
        data.setdefault("records", [])
        data["total_records"] = len(data["records"])
        return data

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
            row.get("ubicacion"),
            row.get("tamano_m2"),
            row.get("habitaciones"),
        )
