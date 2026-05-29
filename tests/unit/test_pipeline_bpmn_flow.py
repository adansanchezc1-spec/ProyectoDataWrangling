import csv

from application.services.pipeline_facade import PipelineFacade
from infrastructure.notifications.email_service import FileLoggerEmailService
from infrastructure.repositories.folder_storage import FolderStorage
from infrastructure.repositories.json_repository import JsonRepository


def _write_csv(path, rows, extra_cols=None):
    fieldnames = [
        "ubicacion",
        "tamano_m2",
        "habitaciones",
        "banos",
        "estrato",
        "precio",
    ]
    if extra_cols:
        fieldnames.extend(extra_cols)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
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
    assert result["total_records"] == 2
    assert result["records_cleaned"] == 1
    assert (tmp_path / "data" / "RAW").exists()
    assert (tmp_path / "data" / "CLEANED").exists()
    assert (tmp_path / "data" / "PROCESSED" / "MDM" / "master_dataset.csv").exists()


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


def test_fecha_column_extracted_from_csv(tmp_path):
    source = tmp_path / "with_fecha.csv"
    _write_csv(
        source,
        [
            {"ubicacion": "Bogota Centro", "tamano_m2": "50", "habitaciones": "2", "banos": "1", "estrato": "3", "precio": "200000000", "fecha": "2020"},
            {"ubicacion": "Bogota Norte", "tamano_m2": "80", "habitaciones": "3", "banos": "2", "estrato": "4", "precio": "300000000", "fecha": "2021"},
            {"ubicacion": "Bogota Sur", "tamano_m2": "60", "habitaciones": "2", "banos": "1", "estrato": "2", "precio": "150000000", "fecha": "2022"},
        ],
        extra_cols=["fecha"],
    )
    result = _facade(tmp_path).run_pipeline(str(source))
    assert result["status"] == "success"
    master = tmp_path / "data" / "PROCESSED" / "MDM" / "master_dataset.csv"
    assert master.exists()
    with master.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    fechas = sorted(int(r["fecha"]) for r in rows if r.get("fecha"))
    assert fechas == [2020, 2021, 2022]


def test_fecha_date_string_extracted_to_year(tmp_path):
    source = tmp_path / "fecha_str.csv"
    _write_csv(
        source,
        [
            {"ubicacion": "Bogota Centro", "tamano_m2": "50", "habitaciones": "2", "banos": "1", "estrato": "3", "precio": "200000000", "fecha": "2023-06-15"},
        ],
        extra_cols=["fecha"],
    )
    result = _facade(tmp_path).run_pipeline(str(source))
    assert result["status"] == "success"
    master = tmp_path / "data" / "PROCESSED" / "MDM" / "master_dataset.csv"
    with master.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    assert rows[0]["fecha"] == "2023"


def test_fecha_missing_does_not_fail(tmp_path):
    source = tmp_path / "no_fecha.csv"
    _write_csv(
        source,
        [
            {"ubicacion": "Bogota Centro", "tamano_m2": "50", "habitaciones": "2", "banos": "1", "estrato": "3", "precio": "200000000"},
        ],
    )
    result = _facade(tmp_path).run_pipeline(str(source))
    assert result["status"] == "success"


def test_batch_accumulates_two_files(tmp_path):
    f1 = tmp_path / "batch1.csv"
    f2 = tmp_path / "batch2.csv"
    _write_csv(
        f1,
        [
            {"ubicacion": "Bogota A", "tamano_m2": "50", "habitaciones": "2", "banos": "1", "estrato": "3", "precio": "100000000", "fecha": "2020"},
        ],
        extra_cols=["fecha"],
    )
    _write_csv(
        f2,
        [
            {"ubicacion": "Bogota B", "tamano_m2": "70", "habitaciones": "3", "banos": "2", "estrato": "4", "precio": "200000000", "fecha": "2021"},
        ],
        extra_cols=["fecha"],
    )
    facade = _facade(tmp_path)
    facade.run_pipeline(str(f1))
    facade.run_pipeline(str(f2))
    master = tmp_path / "data" / "PROCESSED" / "MDM" / "master_dataset.csv"
    with master.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    assert len(rows) == 2
    ubicaciones = {r["ubicacion"] for r in rows}
    assert ubicaciones == {"bogota a", "bogota b"}


def test_batch_mixed_success_rejection(tmp_path):
    valid = tmp_path / "ok.csv"
    rejected = tmp_path / "bad.csv"
    _write_csv(valid, [{"ubicacion": "Bogota C", "tamano_m2": "50", "habitaciones": "2", "banos": "1", "estrato": "3", "precio": "100000000"}])
    _write_csv(rejected, [{"ubicacion": "Cali", "tamano_m2": "50", "habitaciones": "2", "banos": "1", "estrato": "3", "precio": "100000000"}])
    facade = _facade(tmp_path)
    r1 = facade.run_pipeline(str(valid))
    r2 = facade.run_pipeline(str(rejected))
    assert r1["status"] == "success"
    assert r2["status"] == "rejected"
    assert r2["gateway_bpmn"] == 2


def test_rejection_sends_email_notification(tmp_path):
    source = tmp_path / "invalid_email.csv"
    _write_csv(
        source,
        [{"ubicacion": "Medellin", "tamano_m2": "50", "habitaciones": "2", "banos": "1", "estrato": "3", "precio": "200000000"}],
    )
    email_dir = tmp_path / "email_logs"
    facade = PipelineFacade(
        JsonRepository(str(tmp_path / "repositories")),
        email_service=FileLoggerEmailService(str(email_dir)),
        folder_storage=FolderStorage(str(tmp_path / "data")),
    )
    result = facade.run_pipeline(str(source), user_email="user@example.com")
    assert result["status"] == "rejected"
    assert result["email_result"]["sent"] is True
    assert result["email_result"]["to"] == "user@example.com"
    email_files = list(email_dir.iterdir())
    assert len(email_files) == 1
    content = email_files[0].read_text(encoding="utf-8")
    assert "rechazado" in content.lower()
    assert "Gateway 2" in content
    assert "Medellin" in content or "RB-001" in content or "Bogot" in content
