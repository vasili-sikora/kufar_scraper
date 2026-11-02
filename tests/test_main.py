import sys
from unittest.mock import MagicMock, patch

import pytest

from exceptions import KufarScraperError
from main import main, parse_args, run_cron


def test_parse_args_default():
    with patch.object(sys, "argv", ["main.py"]):
        args = parse_args()
        assert args.cron is False


def test_parse_args_cron_flag():
    with patch.object(sys, "argv", ["main.py", "--cron"]):
        args = parse_args()
        assert args.cron is True


@patch("main.setup_logging")
@patch("main.init_db")
@patch("main.KufarClient")
@patch("main.get_service")
def test_run_cron_success(
    mock_get_service: MagicMock,
    mock_kufar_client_cls: MagicMock,
    mock_init_db: MagicMock,
    mock_setup_logging: MagicMock,
):
    mock_service = MagicMock()
    mock_client = MagicMock()

    mock_get_service.return_value.__enter__.return_value = mock_service
    mock_kufar_client_cls.return_value.__enter__.return_value = mock_client

    run_cron()

    mock_setup_logging.assert_called_once_with("cron")
    mock_init_db.assert_called_once()
    mock_service.sync_ads_to_db.assert_called_once_with(mock_client)
    mock_service.export_ads.assert_called_once()


@patch("main.setup_logging")
@patch("main.init_db")
@patch("main.KufarClient")
@patch("main.get_service")
def test_run_cron_handles_scraper_error(
    mock_get_service: MagicMock,
    mock_kufar_client_cls: MagicMock,
    mock_init_db: MagicMock,
    mock_setup_logging: MagicMock,
):
    mock_service = MagicMock()
    mock_client = MagicMock()

    mock_get_service.return_value.__enter__.return_value = mock_service
    mock_kufar_client_cls.return_value.__enter__.return_value = mock_client
    mock_service.sync_ads_to_db.side_effect = KufarScraperError("Failed to fetch")

    with pytest.raises(SystemExit) as exc_info:
        run_cron()

    assert exc_info.value.code == 1


@patch("main.parse_args")
@patch("main.run_cron")
@patch("main.run_interactive")
def test_main_routes_to_cron(
    mock_run_interactive: MagicMock,
    mock_run_cron: MagicMock,
    mock_parse_args: MagicMock,
):
    mock_parse_args.return_value.cron = True

    main()

    mock_run_cron.assert_called_once()
    mock_run_interactive.assert_not_called()


@patch("main.parse_args")
@patch("main.run_cron")
@patch("main.run_interactive")
def test_main_routes_to_interactive(
    mock_run_interactive: MagicMock,
    mock_run_cron: MagicMock,
    mock_parse_args: MagicMock,
):
    mock_parse_args.return_value.cron = False

    main()

    mock_run_interactive.assert_called_once()
    mock_run_cron.assert_not_called()
