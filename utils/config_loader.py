"""
File: config_loader.py

Purpose:
Loads and exposes project configuration settings from the config/config.json file.
Supports runtime environment overrides (development, qa, production) and exposes
variables for browser settings, timeouts, logs, reports, and screenshots.

Author: <Your Name>

Created: 2026-06-19
"""

import json
import os
from pathlib import Path


class ConfigLoader:
    """
    Utility class to load, parse, and serve configuration settings.
    Implements a singleton pattern to ensure settings are parsed once.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        # Resolve config.json path relative to this script directory
        current_dir = Path(__file__).parent.parent
        config_path = current_dir / "config" / "config.json"

        # Safe parsing of the central JSON configuration file
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")

        with open(config_path, "r", encoding="utf-8") as config_file:
            self._config_data = json.load(config_file)

        # Environment resolution: check environment variable before checking config default
        self._environment = os.getenv(
            "TEST_ENV", self._config_data.get("default_environment", "qa")
        ).lower()

        # Validate that the selected environment is configured
        if self._environment not in self._config_data["environments"]:
            raise ValueError(
                f"Selected environment '{self._environment}' is not configured in config.json."
            )

    @property
    def environment(self) -> str:
        """Returns the active environment name."""
        return self._environment

    @property
    def base_url(self) -> str:
        """Returns the URL of the selected target environment."""
        return self._config_data["environments"][self._environment]["base_url"]

    @property
    def browser(self) -> str:
        """Returns the default browser configuration."""
        return self._config_data.get("default_browser", "chrome")

    @property
    def headless(self) -> bool:
        """Returns whether execution should run in headless mode."""
        return self._config_data.get("headless", True)

    @property
    def implicit_wait(self) -> int:
        """Returns implicit wait timeout in seconds."""
        return self._config_data.get("implicit_wait_seconds", 10)

    @property
    def explicit_wait(self) -> int:
        """Returns explicit wait timeout in seconds."""
        return self._config_data.get("explicit_wait_seconds", 15)

    @property
    def retry_count(self) -> int:
        """Returns number of test retries for failing tests."""
        return int(os.getenv("RETRY_COUNT", self._config_data.get("retry_count", 2)))

    @property
    def reports_dir(self) -> Path:
        """Returns the reports directory path."""
        path_str = self._config_data["paths"].get("reports_dir", "reports")
        path = Path(__file__).parent.parent / path_str
        path.mkdir(exist_ok=True)
        return path

    @property
    def screenshots_dir(self) -> Path:
        """Returns the screenshots directory path."""
        path_str = self._config_data["paths"].get("screenshots_dir", "screenshots")
        path = Path(__file__).parent.parent / path_str
        path.mkdir(exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        """Returns the logs directory path."""
        path_str = self._config_data["paths"].get("logs_dir", "logs")
        path = Path(__file__).parent.parent / path_str
        path.mkdir(exist_ok=True)
        return path

    @property
    def log_file(self) -> Path:
        """Returns the path to the automation log file."""
        path_str = self._config_data["paths"].get("log_file", "logs/automation.log")
        path = Path(__file__).parent.parent / path_str
        path.parent.mkdir(exist_ok=True)
        return path

    @property
    def email_config(self) -> dict:
        """Returns email configuration dictionary."""
        return self._config_data.get("email_config", {"enabled": False})
