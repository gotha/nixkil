"""Tests for NixOS tools."""

import pytest
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.nixos import (
    nixos_option_search,
    nixos_option_info,
    nixos_rebuild,
    nixos_generations,
)


class TestNixosOptionSearch:
    """Tests for nixos_option_search function."""

    @patch("tools.nixos._run_command")
    def test_search_returns_suggestion(self, mock_run):
        """Test that search returns helpful suggestion on failure."""
        mock_run.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "error",
            "returncode": 1,
        }

        result = nixos_option_search("nginx")

        assert result["success"] is True
        assert "suggestion" in result
        assert "nginx" in result["suggestion"]


class TestNixosOptionInfo:
    """Tests for nixos_option_info function."""

    @patch("tools.nixos._run_command")
    def test_info_returns_option_details(self, mock_run):
        """Test that info returns option details."""
        mock_run.return_value = {
            "success": True,
            "stdout": "Value: true\nType: boolean\nDescription: Enable nginx",
            "stderr": "",
            "returncode": 0,
        }

        result = nixos_option_info("services.nginx.enable")

        assert result["success"] is True
        assert result["option"] == "services.nginx.enable"
        assert "info" in result

    @patch("tools.nixos._run_command")
    def test_info_provides_fallback(self, mock_run):
        """Test that info provides documentation link on failure."""
        mock_run.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "command not found",
            "returncode": 127,
        }

        result = nixos_option_info("services.nginx.enable")

        assert result["success"] is True
        assert "documentation" in result


class TestNixosRebuild:
    """Tests for nixos_rebuild function."""

    def test_invalid_action_rejected(self):
        """Test that invalid actions are rejected."""
        result = nixos_rebuild(action="invalid")

        assert result["success"] is False
        assert "Invalid action" in result["error"]

    def test_valid_actions_accepted(self):
        """Test that valid actions are accepted in dry run."""
        valid_actions = ["switch", "boot", "test", "build", "dry-activate", "dry-build"]

        for action in valid_actions:
            result = nixos_rebuild(action=action, dry_run=True)
            # Dry run should always succeed without running anything
            assert result["success"] is True

    def test_dry_run_returns_command(self):
        """Test that dry run returns the command that would be run."""
        result = nixos_rebuild(action="switch", dry_run=True)

        assert result["success"] is True
        assert "command" in result
        assert "nixos-rebuild" in result["command"]
        assert "switch" in result["command"]

    def test_flake_config_in_command(self):
        """Test that flake config is included in command."""
        result = nixos_rebuild(
            action="switch",
            flake="/etc/nixos",
            hostname="myhost",
            dry_run=True,
        )

        assert result["success"] is True
        assert "--flake" in result["command"]


class TestNixosGenerations:
    """Tests for nixos_generations function."""

    @patch("tools.nixos._run_command")
    def test_generations_returns_list(self, mock_run):
        """Test that generations returns a list."""
        mock_run.return_value = {
            "success": True,
            "stdout": """   1   2024-01-01 12:00:00
   2   2024-01-02 12:00:00
   3   2024-01-03 12:00:00   (current)
""",
            "stderr": "",
            "returncode": 0,
        }

        result = nixos_generations()

        assert result["success"] is True
        assert "generations" in result
        assert len(result["generations"]) == 3

    @patch("tools.nixos._run_command")
    def test_generations_identifies_current(self, mock_run):
        """Test that current generation is identified."""
        mock_run.return_value = {
            "success": True,
            "stdout": """   1   2024-01-01 12:00:00
   2   2024-01-02 12:00:00   (current)
""",
            "stderr": "",
            "returncode": 0,
        }

        result = nixos_generations()

        assert result["success"] is True
        current = [g for g in result["generations"] if g["current"]]
        assert len(current) == 1
        assert current[0]["id"] == "2"

    @patch("tools.nixos._run_command")
    def test_generations_respects_limit(self, mock_run):
        """Test that limit parameter is respected."""
        lines = [f"   {i}   2024-01-{i:02d} 12:00:00" for i in range(1, 21)]
        mock_run.return_value = {
            "success": True,
            "stdout": "\n".join(lines),
            "stderr": "",
            "returncode": 0,
        }

        result = nixos_generations(limit=5)

        assert result["success"] is True
        assert len(result["generations"]) == 5
        assert result["total"] == 20

