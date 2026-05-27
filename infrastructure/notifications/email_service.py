"""EmailService skeleton using SMTP (configurable)"""
import smtplib
from typing import Optional


class EmailService:
    def __init__(self, host: str = "localhost", port: int = 25, username: Optional[str] = None, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, subject: str, body: str, to: str) -> None:
        # Placeholder: simple SMTP send (to be implemented with proper headers)
        raise NotImplementedError
