from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_main_help():
    """Test main function with --help argument."""
    with patch("sys.argv", ["main.py", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            from src.main import main

            await main()
        # SystemExit with code 0 for --help is normal
        assert excinfo.value.code == 0


@pytest.mark.asyncio
async def test_main_no_action():
    """Test main function with no action specified."""
    with (
        patch("sys.argv", ["main.py"]),
        patch("argparse.ArgumentParser.print_help") as mock_print_help,
        patch("src.main.logger") as mock_logger,
    ):
        from src.main import main

        await main()

        mock_logger.warning.assert_called_once()
        mock_print_help.assert_called_once()


@pytest.mark.asyncio
async def test_launch_tui_import_error():
    """Test launch_tui when TUI dependencies are not available."""
    with (
        patch.dict("sys.modules", {"src.tui.app": None}),
        patch("src.main.logger") as mock_logger,
        patch("sys.exit") as mock_exit,
    ):
        from src.main import launch_tui

        await launch_tui()

        mock_logger.error.assert_called_once()
        mock_exit.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_app_version():
    """Test get_app_version function."""
    from src.main import get_app_version

    version = await get_app_version()
    assert isinstance(version, str)
    assert len(version) > 0


@pytest.mark.asyncio
async def test_export_to_csv():
    """Test CSV export functionality."""
    with (
        patch("src.main.DatabaseManager") as mock_db_manager,
        patch("src.main.logger") as mock_logger,
    ):
        from src.main import export_to_csv

        await export_to_csv("test.csv", "test.db")

        mock_db_manager.assert_called_once_with(db_path="test.db")
        mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_export_to_json():
    """Test JSON export functionality."""
    with (
        patch("src.main.DatabaseManager") as mock_db_manager,
        patch("src.main.logger") as mock_logger,
    ):
        from src.main import export_to_json

        await export_to_json("test.json", "test.db")

        mock_db_manager.assert_called_once_with(db_path="test.db")
        mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_export_to_markdown():
    """Test Markdown export functionality."""
    with (
        patch("src.main.DatabaseManager") as mock_db_manager,
        patch("src.main.logger") as mock_logger,
    ):
        from src.main import export_to_markdown

        await export_to_markdown("test.md", "test.db")

        mock_db_manager.assert_called_once_with(db_path="test.db")
        mock_logger.info.assert_called()
