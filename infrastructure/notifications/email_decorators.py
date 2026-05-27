"""Email decorators: ValidacionEmailDecorator and NotificacionInsercionDecorator"""
from typing import Protocol


class IEmailService(Protocol):
    def send(self, subject: str, body: str, to: str) -> None:
        ...


class EmailDecorator:
    def __init__(self, wrapped: IEmailService):
        self._wrapped = wrapped

    def send(self, subject: str, body: str, to: str) -> None:
        self._wrapped.send(subject, body, to)


class ValidacionEmailDecorator(EmailDecorator):
    def send(self, subject: str, body: str, to: str) -> None:
        # Simple validation placeholder
        if "@" not in to or "." not in to.split("@")[-1]:
            raise ValueError("Invalid email address")
        super().send(subject, body, to)


class NotificacionInsercionDecorator(EmailDecorator):
    def send(self, subject: str, body: str, to: str) -> None:
        # Add insertion-specific template or headers
        templated_body = f"[Insertion]\n{body}"
        super().send(subject, templated_body, to)
