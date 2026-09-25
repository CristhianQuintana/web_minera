import logging
import sys

SENSITIVE = ("password", "token", "secret", "authorization", "service_role")


class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        lowered = message.lower()
        if any(word in lowered for word in SENSITIVE):
            return "[redacted]"
        return message


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("web_minera")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(SafeFormatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
