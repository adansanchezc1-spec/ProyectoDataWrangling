import csv

from application.services.pipeline_facade import PipelineFacade
from infrastructure.repositories.folder_storage import FolderStorage
from infrastructure.repositories.json_repository import JsonRepository


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "ubicacion",
                "tamano_m2",
                "habitaciones",
                "banos",
                "estrato",
                "precio",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _facade(tmp_path):
    return PipelineFacade(
        JsonRepository(str(tmp_path / "repositories")),
        folder_storage=FolderStorage(str(tmp_path / "data")),
    )


def test_pipeline_persists_raw_cleaned_and_mdm(tmp_path):
    source = tmp_path / "valid.csv"
    _write_csv(
        source,
        [
            {
                "ubicacion": "Bogota Centro",
                "tamano_m2": "50",
                "habitaciones": "2",
                "banos": "1",
                "estrato": "3",
                "precio": "200000000",
            },
            {
                "ubicacion": "Bogota Centro",
                "tamano_m2": "50",
                "habitaciones": "2",
                "banos": "1",
                "estrato": "3",
                "precio": "200000000",
            },
        ],
    )

    result = _facade(tmp_path).run_pipeline(str(source))

    assert result["status"] == "success"
    assert result["records_cleaned"] == 1
    assert (tmp_path / "data" / "RAW").exists()
    assert (tmp_path / "data" / "CLEANED").exists()
    assert (tmp_path / "data" / "PROCESSED" / "MDM" / "master_dataset.json").exists()


def test_pipeline_rejects_non_bogota_dataset(tmp_path):
    source = tmp_path / "invalid.csv"
    _write_csv(
        source,
        [
            {
                "ubicacion": "Medellin",
                "tamano_m2": "50",
                "habitaciones": "2",
                "banos": "1",
                "estrato": "3",
                "precio": "200000000",
            }
        ],
    )

    result = _facade(tmp_path).run_pipeline(str(source))

    assert result["status"] == "rejected"
    assert result["gateway_bpmn"] == 2
    assert (tmp_path / "data" / "REJECTED").exists()


def test_pipeline_rejects_semantically_incoherent_dataset(tmp_path):
    source = tmp_path / "invalid_quality.csv"
    _write_csv(
        source,
        [
            {
                "ubicacion": "Bogota Centro",
                "tamano_m2": "-50",
                "habitaciones": "2",
                "banos": "1",
                "estrato": "3",
                "precio": "200000000",
            }
        ],
    )

    result = _facade(tmp_path).run_pipeline(str(source))

    assert result["status"] == "rejected"
    assert result["gateway_bpmn"] == 4
