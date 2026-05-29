from datetime import datetime

from domain.entities import Dataset, RejectionLog
from infrastructure.repositories.folder_storage import FolderStorage


def _dataset(dataset_id="ds1"):
    return Dataset(
        id=dataset_id,
        source_path="sample.csv",
        format="CSV",
        status="CLEANED",
        created_at=datetime.utcnow(),
        schema={
            "ubicacion": "str",
            "tamano_m2": "float",
            "habitaciones": "int",
            "banos": "int",
            "estrato": "int",
            "precio": "float",
        },
        records=[
            {
                "ubicacion": "bogota centro",
                "tamano_m2": 50.0,
                "habitaciones": 2,
                "banos": 1,
                "estrato": 3,
                "precio": 200000000.0,
            }
        ],
        rows_preview=[],
        total_rows=1,
    )


def test_folder_storage_persists_bpmn_folders(tmp_path):
    storage = FolderStorage(str(tmp_path))
    dataset = _dataset()

    raw_path = storage.persist_raw(dataset)
    cleaned_path = storage.persist_cleaned(dataset)
    mdm_path = storage.append_to_master(dataset)

    assert raw_path.exists()
    assert cleaned_path.exists()
    assert mdm_path.exists()
    assert raw_path.parent.name == "RAW"
    assert cleaned_path.parent.name == "CLEANED"
    assert mdm_path.parent.name == "MDM"


def test_folder_storage_persists_rejection_details(tmp_path):
    storage = FolderStorage(str(tmp_path))
    rejection = RejectionLog(
        id="rej1",
        dataset_id="ds1",
        motivo="Formato invalido",
        gateway_bpmn=2,
        regla_negocio="RB-004",
    )

    rejection_path = storage.persist_rejection(rejection)

    assert rejection_path.exists()
    assert rejection_path.parent.name == "REJECTED"


def test_folder_storage_keeps_single_master_table_without_duplicates(tmp_path):
    storage = FolderStorage(str(tmp_path))
    dataset = _dataset()

    storage.append_to_master(dataset)
    master_path = storage.append_to_master(dataset)

    content = master_path.read_text(encoding="utf-8")
    assert "ubicacion;tamano_m2;habitaciones;banos;estrato;precio" in content
    assert content.count("bogota centro") == 1

    meta_path = tmp_path / "PROCESSED" / "MDM" / "master_metadata.json"
    assert meta_path.exists()
    import json
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["total_records"] == 1
