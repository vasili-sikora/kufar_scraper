import logging
import os
from unittest.mock import patch

from logger import setup_logging


def test_setup_logging_without_console(tmp_path):
    with (
        patch("logger.LOGS_DIR", tmp_path),
        patch.dict(os.environ, {"ENABLE_CLI_LOGS": "false"}, clear=True),
    ):
        setup_logging("cli")

        root_logger = logging.getLogger()
        handler_types = [type(h) for h in root_logger.handlers]
        assert logging.StreamHandler not in handler_types
        assert any(h.__class__.__name__ == "RotatingFileHandler" for h in root_logger.handlers)


def test_setup_logging_with_enable_cli_logs(tmp_path):
    with (
        patch("logger.LOGS_DIR", tmp_path),
        patch.dict(os.environ, {"ENABLE_CLI_LOGS": "true"}, clear=True),
    ):
        setup_logging("cli")

        root_logger = logging.getLogger()
        handler_types = [type(h) for h in root_logger.handlers]
        assert logging.StreamHandler in handler_types
