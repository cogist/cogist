"""Tests for ConfigManager and platform utilities"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from cogist.infrastructure.utils import PLATFORM, ConfigManager


class TestPlatform:
    """Test suite for platform utilities"""

    def test_platform_constant_exists(self):
        """Test that PLATFORM constant is defined"""
        assert PLATFORM is not None
        assert isinstance(PLATFORM, str)

    def test_platform_valid_value(self):
        """Test that PLATFORM has a valid value"""
        valid_platforms = ["Darwin", "Windows", "Linux"]
        assert PLATFORM in valid_platforms


class TestConfigManager:
    """Test suite for ConfigManager"""

    def setup_method(self):
        """Create a temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "config.json"

    def teardown_method(self):
        """Clean up temporary files"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_config_manager(self) -> ConfigManager:
        """Create a ConfigManager with custom config file path"""
        manager = ConfigManager.__new__(ConfigManager)
        manager.config_file = self.config_file
        manager.config = {}
        return manager

    def test_get_default_value(self):
        """Test getting a value with default"""
        manager = self._create_config_manager()

        result = manager.get("nonexistent_key", "default_value")

        assert result == "default_value"

    def test_set_and_get_value(self):
        """Test setting and getting a value"""
        manager = self._create_config_manager()

        manager.set("test_key", "test_value")
        result = manager.get("test_key")

        assert result == "test_value"

    def test_set_overwrites_value(self):
        """Test that set overwrites existing value"""
        manager = self._create_config_manager()

        manager.set("key", "value1")
        manager.set("key", "value2")
        result = manager.get("key")

        assert result == "value2"

    def test_save_creates_file(self):
        """Test that save creates the config file"""
        manager = self._create_config_manager()

        manager.set("test_key", "test_value")
        manager.save()

        assert self.config_file.exists()

    def test_save_writes_valid_json(self):
        """Test that save writes valid JSON"""
        manager = self._create_config_manager()

        manager.set("string_key", "string_value")
        manager.set("int_key", 42)
        manager.set("bool_key", True)
        manager.save()

        # Read and parse the file
        data = json.loads(self.config_file.read_text())

        assert data["string_key"] == "string_value"
        assert data["int_key"] == 42
        assert data["bool_key"] is True

    def test_load_reads_existing_file(self):
        """Test that load reads an existing config file"""
        # Create a config file manually
        test_data = {"loaded_key": "loaded_value"}
        self.config_file.write_text(json.dumps(test_data))

        manager = self._create_config_manager()
        manager.load()

        assert manager.get("loaded_key") == "loaded_value"

    def test_load_handles_missing_file(self):
        """Test that load handles missing file gracefully"""
        manager = self._create_config_manager()

        # Should not raise an error
        manager.load()

        assert manager.config == {}

    def test_load_handles_invalid_json(self):
        """Test that load handles invalid JSON gracefully"""
        self.config_file.write_text("invalid json{")

        manager = self._create_config_manager()

        # Should not raise an error
        manager.load()

        assert manager.config == {}

    def test_round_trip_save_load(self):
        """Test that save and load are inverse operations"""
        manager = self._create_config_manager()

        original_data = {
            "string": "test",
            "number": 123,
            "boolean": True,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        for key, value in original_data.items():
            manager.set(key, value)

        manager.save()

        # Create a new manager and load
        manager2 = self._create_config_manager()
        manager2.load()

        for key, value in original_data.items():
            assert manager2.get(key) == value

    @patch("cogist.infrastructure.utils.config_manager.PLATFORM", "Darwin")
    def test_get_template_directory_macos(self):
        """Test template directory path on macOS"""
        manager = self._create_config_manager()

        # Use temp_dir as home to avoid permission issues
        with patch.object(Path, "home", return_value=Path(self.temp_dir)):
            template_dir = manager.get_template_directory()

        expected = Path(self.temp_dir) / "Library" / "Application Support" / "cogist" / "templates"
        assert template_dir == expected
        assert template_dir.exists()  # Should be created

    @patch("cogist.infrastructure.utils.config_manager.PLATFORM", "Windows")
    def test_get_template_directory_windows(self):
        """Test template directory path on Windows"""
        manager = self._create_config_manager()

        # Use temp_dir to avoid path issues
        with (
            patch.dict(os.environ, {"APPDATA": str(self.temp_dir)}),
            patch.object(Path, "home", return_value=Path(self.temp_dir)),
        ):
            template_dir = manager.get_template_directory()

        expected = Path(self.temp_dir) / "cogist" / "templates"
        assert template_dir == expected
        assert template_dir.exists()  # Should be created

    @patch("cogist.infrastructure.utils.config_manager.PLATFORM", "Linux")
    def test_get_template_directory_linux(self):
        """Test template directory path on Linux"""
        manager = self._create_config_manager()

        # Use temp_dir as home to avoid permission issues
        with patch.object(Path, "home", return_value=Path(self.temp_dir)):
            template_dir = manager.get_template_directory()

        expected = Path(self.temp_dir) / ".local" / "share" / "cogist" / "templates"
        assert template_dir == expected
        assert template_dir.exists()  # Should be created

    def test_get_template_directory_custom_path(self):
        """Test template directory with custom path from config"""
        manager = self._create_config_manager()

        custom_path = "/custom/template/path"
        manager.set("template_directory", custom_path)

        template_dir = manager.get_template_directory()

        assert template_dir == Path(custom_path)

    def test_get_template_directory_creates_folder(self):
        """Test that get_template_directory creates the folder if it doesn't exist"""
        manager = self._create_config_manager()

        with (
            patch.object(Path, "home", return_value=Path(self.temp_dir)),
            patch("cogist.infrastructure.utils.config_manager.PLATFORM", "Darwin"),
        ):
            template_dir = manager.get_template_directory()

        assert template_dir.exists()
        assert template_dir.is_dir()
