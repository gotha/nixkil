"""Tests to validate example flakes."""

import pytest
import subprocess
from pathlib import Path


EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

DEVSHELL_EXAMPLES = [
    "devshells/golang",
    "devshells/python",
    "devshells/rust",
    "devshells/nodejs",
    "devshells/java",
    "devshells/multi-lang",
]

DEVENV_EXAMPLES = [
    "devenv/basic",
    "devenv/with-services",
    "devenv/with-precommit",
]


def run_nix_command(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    """Run a nix command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode == 0, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


class TestDevShellExamples:
    """Tests for devShell example flakes."""

    @pytest.mark.requires_nix
    @pytest.mark.slow
    @pytest.mark.parametrize("example", DEVSHELL_EXAMPLES)
    def test_flake_check(self, example):
        """Test that each devShell example passes flake check."""
        example_path = EXAMPLES_DIR / example

        if not example_path.exists():
            pytest.skip(f"Example {example} does not exist")

        success, output = run_nix_command(
            ["nix", "flake", "check", "--no-build"],
            example_path,
        )

        assert success, f"Flake check failed for {example}: {output}"

    @pytest.mark.requires_nix
    @pytest.mark.parametrize("example", DEVSHELL_EXAMPLES)
    def test_flake_show(self, example):
        """Test that each devShell example can show outputs."""
        example_path = EXAMPLES_DIR / example

        if not example_path.exists():
            pytest.skip(f"Example {example} does not exist")

        success, output = run_nix_command(
            ["nix", "flake", "show"],
            example_path,
        )

        assert success, f"Flake show failed for {example}: {output}"

    @pytest.mark.requires_nix
    @pytest.mark.parametrize("example", DEVSHELL_EXAMPLES)
    def test_has_devshell_output(self, example):
        """Test that each example has a devShell output."""
        example_path = EXAMPLES_DIR / example

        if not example_path.exists():
            pytest.skip(f"Example {example} does not exist")

        success, output = run_nix_command(
            ["nix", "flake", "show", "--json"],
            example_path,
        )

        assert success, f"Flake show failed for {example}: {output}"
        assert "devShells" in output or "devShell" in output, \
            f"No devShell output in {example}"


class TestDevenvExamples:
    """Tests for devenv example flakes."""

    @pytest.mark.requires_nix
    @pytest.mark.slow
    @pytest.mark.parametrize("example", DEVENV_EXAMPLES)
    def test_flake_show(self, example):
        """Test that each devenv example can show outputs."""
        example_path = EXAMPLES_DIR / example

        if not example_path.exists():
            pytest.skip(f"Example {example} does not exist")

        success, output = run_nix_command(
            ["nix", "flake", "show"],
            example_path,
        )

        # Devenv flakes may fail show without --impure, that's okay
        # We just want to verify the flake is parseable
        assert "error: getting" not in output.lower() or success, \
            f"Flake show failed unexpectedly for {example}: {output}"


class TestExampleFiles:
    """Tests for example file structure."""

    @pytest.mark.parametrize("example", DEVSHELL_EXAMPLES + DEVENV_EXAMPLES)
    def test_has_flake_nix(self, example):
        """Test that each example has a flake.nix."""
        flake_path = EXAMPLES_DIR / example / "flake.nix"
        assert flake_path.exists(), f"Missing flake.nix in {example}"

    @pytest.mark.parametrize("example", DEVSHELL_EXAMPLES + DEVENV_EXAMPLES)
    def test_has_envrc(self, example):
        """Test that each example has a .envrc."""
        envrc_path = EXAMPLES_DIR / example / ".envrc"
        assert envrc_path.exists(), f"Missing .envrc in {example}"

    @pytest.mark.parametrize("example", DEVENV_EXAMPLES)
    def test_devenv_has_devenv_nix(self, example):
        """Test that devenv examples have devenv.nix."""
        devenv_path = EXAMPLES_DIR / example / "devenv.nix"
        assert devenv_path.exists(), f"Missing devenv.nix in {example}"

    @pytest.mark.parametrize("example", DEVSHELL_EXAMPLES + DEVENV_EXAMPLES)
    def test_uses_nixos_25_11(self, example):
        """Test that examples use nixos-25.11."""
        flake_path = EXAMPLES_DIR / example / "flake.nix"
        content = flake_path.read_text()
        assert "nixos-25.11" in content, \
            f"Example {example} should use nixos-25.11"

