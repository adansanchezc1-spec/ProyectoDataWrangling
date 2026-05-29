from unittest.mock import MagicMock

from domain.exceptions import NotificacionException
from infrastructure.notifications.email_decorators import (
    NotificacionInsercionDecorator,
    ValidacionEmailDecorator,
)


def _mock_service():
    svc = MagicMock()
    svc.send.return_value = True
    svc.validate_email.return_value = True
    return svc


def test_validacion_decorator_rejects_invalid_email():
    wrapped = _mock_service()
    decorator = ValidacionEmailDecorator(wrapped)
    try:
        decorator.send("subj", "body", "not-an-email")
        assert False, "Expected NotificacionException"
    except NotificacionException:
        pass
    wrapped.send.assert_not_called()


def test_validacion_decorator_accepts_valid_email():
    wrapped = _mock_service()
    decorator = ValidacionEmailDecorator(wrapped)
    result = decorator.send("subj", "body", "user@example.com")
    assert result is True
    wrapped.send.assert_called_once_with("subj", "body", "user@example.com")


def test_validacion_decorator_validates_multiple_emails():
    wrapped = _mock_service()
    decorator = ValidacionEmailDecorator(wrapped)
    result = decorator.send("subj", "body", "a@b.com, c@d.com")
    assert result is True
    wrapped.send.assert_called_once_with("subj", "body", "a@b.com, c@d.com")


def test_notificacion_decorator_enriches_subject():
    wrapped = _mock_service()
    decorator = NotificacionInsercionDecorator(wrapped)
    decorator.send("My Subject", "body", "user@example.com")
    args, _ = wrapped.send.call_args
    assert "[Data Wrangling - MDM Insertion]" in args[0]
    assert "My Subject" in args[0]


def test_notificacion_decorator_enriches_body():
    wrapped = _mock_service()
    decorator = NotificacionInsercionDecorator(wrapped)
    decorator.send("subj", "original body", "user@example.com")
    args, _ = wrapped.send.call_args
    assert "original body" in args[1]
    assert "Data Wrangling" in args[1]
    assert "Inserción procesada" in args[1]


def test_decorators_chain_correctly():
    wrapped = _mock_service()
    decorator = NotificacionInsercionDecorator(
        ValidacionEmailDecorator(wrapped)
    )
    result = decorator.send("subj", "body", "user@example.com")
    assert result is True
    wrapped.send.assert_called_once()


def test_send_delegated_to_wrapped_service():
    wrapped = _mock_service()
    decorator = ValidacionEmailDecorator(wrapped)
    decorator.send("subj", "body", "a@b.com")
    wrapped.send.assert_called_once_with("subj", "body", "a@b.com")
