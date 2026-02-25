"""Tests for package management tools."""

import pytest
from unittest.mock import patch, MagicMock
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.packages import (
    nix_search,
    nix_package_info,
    nix_run,
    nix_shell,
    nix_build,
    _run_command,
)


class TestRunCommand:
    """Tests for the _run_command helper."""

    def test_successful_command(self):
        """Test running a successful command."""
        result = _run_command(["echo", "hello"])
        assert result["success"] is True
        assert "hello" in result["stdout"]
        assert result["returncode"] == 0

    def test_failed_command(self):
        """Test running a failing command."""
        result = _run_command(["false"])
        assert result["success"] is False
        assert result["returncode"] != 0

    def test_nonexistent_command(self):
        """Test running a nonexistent command."""
        result = _run_command(["nonexistent_command_xyz"])
        assert result["success"] is False
        assert "error" in result


class TestNixSearch:
    """Tests for nix_search function."""

    @patch("tools.packages._run_command")
    def test_search_returns_packages(self, mock_run):
        """Test that search returns parsed packages."""
        mock_run.return_value = {
            "success": True,
            "stdout": json.dumps({
                "nixpkgs#hello": {"description": "A program that prints Hello, world!"},
                "nixpkgs#cowsay": {"description": "Generates ASCII pictures of a cow"},
            }),
            "stderr": "",
            "returncode": 0,
        }

        result = nix_search("hello")

        assert result["success"] is True
        assert "packages" in result
        assert len(result["packages"]) == 2

    @patch("tools.packages._run_command")
    def test_search_respects_max_results(self, mock_run):
        """Test that max_results limits output."""
        packages = {f"nixpkgs#pkg{i}": {"description": f"Package {i}"} for i in range(30)}
        mock_run.return_value = {
            "success": True,
            "stdout": json.dumps(packages),
            "stderr": "",
            "returncode": 0,
        }

        result = nix_search("pkg", max_results=5)

        assert result["success"] is True
        assert result["returned"] == 5
        assert result["total_found"] == 30

    @patch("tools.packages._run_command")
    def test_search_handles_failure(self, mock_run):
        """Test search handles command failure."""
        mock_run.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "error: flake not found",
            "returncode": 1,
        }

        result = nix_search("nonexistent")

        assert result["success"] is False


class TestNixPackageInfo:
    """Tests for nix_package_info function."""

    @patch("tools.packages._run_command")
    def test_package_info_returns_meta(self, mock_run):
        """Test that package info returns metadata."""
        mock_run.return_value = {
            "success": True,
            "stdout": json.dumps({
                "description": "A program that prints Hello, world!",
                "homepage": "https://www.gnu.org/software/hello/",
                "license": {"spdxId": "GPL-3.0-or-later"},
            }),
            "stderr": "",
            "returncode": 0,
        }

        result = nix_package_info("hello")

        assert result["success"] is True
        assert result["package"] == "hello"
        assert "meta" in result
        assert "description" in result["meta"]


class TestNixBuild:
    """Tests for nix_build function."""

    @patch("tools.packages._run_command")
    def test_build_returns_paths(self, mock_run):
        """Test that build returns output paths."""
        mock_run.return_value = {
            "success": True,
            "stdout": "/nix/store/abc123-hello-2.10\n",
            "stderr": "",
            "returncode": 0,
        }

        result = nix_build("nixpkgs#hello", no_link=True)

        assert result["success"] is True
        assert "output_paths" in result
        assert "/nix/store/abc123-hello-2.10" in result["output_paths"]

    @patch("tools.packages._run_command")
    def test_build_handles_failure(self, mock_run):
        """Test build handles failure."""
        mock_run.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "error: build failed",
            "returncode": 1,
        }

        result = nix_build("nixpkgs#nonexistent")

        assert result["success"] is False

