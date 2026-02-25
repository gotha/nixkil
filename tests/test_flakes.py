"""Tests for flake tools."""

import pytest
from unittest.mock import patch
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.flakes import (
    flake_init,
    flake_show,
    flake_check,
    flake_update,
    flake_lock_info,
)


class TestFlakeInit:
    """Tests for flake_init function."""

    @patch("tools.flakes._run_command")
    def test_init_creates_flake(self, mock_run):
        """Test that init creates a flake."""
        mock_run.return_value = {
            "success": True,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

        result = flake_init("/tmp/test")

        assert result["success"] is True
        assert "flake.nix" in result["files_created"]
        mock_run.assert_called_once()

    @patch("tools.flakes._run_command")
    def test_init_with_template(self, mock_run):
        """Test init with a template."""
        mock_run.return_value = {
            "success": True,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

        result = flake_init("/tmp/test", template="templates#python")

        assert result["success"] is True
        # Verify template was passed to command
        call_args = mock_run.call_args[0][0]
        assert "--template" in call_args
        assert "templates#python" in call_args


class TestFlakeShow:
    """Tests for flake_show function."""

    @patch("tools.flakes._run_command")
    def test_show_returns_outputs(self, mock_run):
        """Test that show returns flake outputs."""
        mock_run.return_value = {
            "success": True,
            "stdout": json.dumps({
                "packages": {
                    "x86_64-linux": {
                        "default": {"type": "derivation"}
                    }
                }
            }),
            "stderr": "",
            "returncode": 0,
        }

        result = flake_show(".")

        assert result["success"] is True
        assert "outputs" in result
        assert "packages" in result["outputs"]

    @patch("tools.flakes._run_command")
    def test_show_handles_non_json(self, mock_run):
        """Test show handles non-JSON output gracefully."""
        mock_run.return_value = {
            "success": True,
            "stdout": "packages:\n  default: derivation",
            "stderr": "",
            "returncode": 0,
        }

        result = flake_show(".")

        assert result["success"] is True
        assert "raw_output" in result


class TestFlakeCheck:
    """Tests for flake_check function."""

    @patch("tools.flakes._run_command")
    def test_check_passes(self, mock_run):
        """Test check on valid flake."""
        mock_run.return_value = {
            "success": True,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

        result = flake_check(".")

        assert result["success"] is True
        assert "passed" in result["message"].lower()

    @patch("tools.flakes._run_command")
    def test_check_fails(self, mock_run):
        """Test check on invalid flake."""
        mock_run.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "error: attribute 'default' missing",
            "returncode": 1,
        }

        result = flake_check(".")

        assert result["success"] is False
        assert "errors" in result


class TestFlakeUpdate:
    """Tests for flake_update function."""

    @patch("tools.flakes._run_command")
    def test_update_all_inputs(self, mock_run):
        """Test updating all inputs."""
        mock_run.return_value = {
            "success": True,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

        result = flake_update(".")

        assert result["success"] is True
        assert result["inputs_updated"] == "all"

    @patch("tools.flakes._run_command")
    def test_update_specific_inputs(self, mock_run):
        """Test updating specific inputs."""
        mock_run.return_value = {
            "success": True,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

        result = flake_update(".", inputs=["nixpkgs"])

        assert result["success"] is True
        assert result["inputs_updated"] == ["nixpkgs"]


class TestFlakeLockInfo:
    """Tests for flake_lock_info function."""

    @patch("tools.flakes._run_command")
    def test_lock_info_returns_inputs(self, mock_run):
        """Test that lock info returns input information."""
        mock_run.return_value = {
            "success": True,
            "stdout": json.dumps({
                "description": "Test flake",
                "locks": {
                    "nodes": {
                        "root": {"inputs": {"nixpkgs": "nixpkgs"}},
                        "nixpkgs": {
                            "locked": {
                                "type": "github",
                                "owner": "NixOS",
                                "repo": "nixpkgs",
                                "rev": "abc123def456",
                                "lastModified": 1704067200,
                            }
                        }
                    }
                }
            }),
            "stderr": "",
            "returncode": 0,
        }

        result = flake_lock_info(".")

        assert result["success"] is True
        assert "inputs" in result
        assert "nixpkgs" in result["inputs"]
        assert result["inputs"]["nixpkgs"]["owner"] == "NixOS"

