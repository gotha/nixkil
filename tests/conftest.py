"""Pytest configuration and shared fixtures."""

import os
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


@pytest.fixture
def sample_flake(temp_dir):
    """Create a sample flake.nix for testing."""
    flake_content = '''{
  description = "Test flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.hello;
  };
}
'''
    flake_path = Path(temp_dir) / "flake.nix"
    flake_path.write_text(flake_content)
    return temp_dir


@pytest.fixture
def sample_nix_file(temp_dir):
    """Create a sample .nix file for testing."""
    nix_content = '''{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [ pkgs.hello ];
}
'''
    nix_path = Path(temp_dir) / "shell.nix"
    nix_path.write_text(nix_content)
    return str(nix_path)


@pytest.fixture
def invalid_nix_file(temp_dir):
    """Create an invalid .nix file for testing error handling."""
    nix_content = '''{ pkgs ? import <nixpkgs> {}

# Missing closing brace - syntax error
pkgs.mkShell {
  packages = [ pkgs.hello ]
'''
    nix_path = Path(temp_dir) / "invalid.nix"
    nix_path.write_text(nix_content)
    return str(nix_path)


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "requires_nix: marks tests that require nix to be installed"
    )
    config.addinivalue_line(
        "markers", "requires_nixos: marks tests that require NixOS"
    )


def has_nix():
    """Check if nix is available."""
    return shutil.which("nix") is not None


def is_nixos():
    """Check if running on NixOS."""
    return os.path.exists("/etc/NIXOS")


@pytest.fixture(autouse=True)
def skip_without_nix(request):
    """Skip tests that require nix if it's not installed."""
    if request.node.get_closest_marker("requires_nix"):
        if not has_nix():
            pytest.skip("Nix is not installed")


@pytest.fixture(autouse=True)
def skip_without_nixos(request):
    """Skip tests that require NixOS if not running on NixOS."""
    if request.node.get_closest_marker("requires_nixos"):
        if not is_nixos():
            pytest.skip("Not running on NixOS")

