from pathlib import Path

from infrastructure.notifications.email_service import FileLoggerEmailService


def test_logger_sends_to_disk(tmp_path):
    logger = FileLoggerEmailService(str(tmp_path))
    result = logger.send("Subject", "Body content", "user@example.com")
    assert result is True
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "To: user@example.com" in content
    assert "Subject: Subject" in content
    assert "Body content" in content


def test_logger_creates_directory(tmp_path):
    nested = tmp_path / "a" / "b" / "c"
    logger = FileLoggerEmailService(str(nested))
    logger.send("subj", "body", "test@test.com")
    assert nested.exists()
    assert len(list(nested.iterdir())) == 1


def test_logger_validates_email():
    logger = FileLoggerEmailService()
    assert logger.validate_email("user@example.com") is True
    assert logger.validate_email("not-an-email") is False
    assert logger.validate_email("") is False


def test_logger_handles_special_chars_in_email(tmp_path):
    logger = FileLoggerEmailService(str(tmp_path))
    result = logger.send("subj", "body", "test+tag@example.com")
    assert result is True
    files = list(tmp_path.iterdir())
    assert len(files) == 1


def test_logger_persists_subject_and_body_exactly(tmp_path):
    logger = FileLoggerEmailService(str(tmp_path))
    logger.send("Exact Subject", "Exact Body\nLine 2", "a@b.com")
    content = list(tmp_path.iterdir())[0].read_text(encoding="utf-8")
    assert "Exact Subject" in content
    assert "Exact Body" in content
    assert "Line 2" in content
