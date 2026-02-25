"""Tests for language analysis tools."""

import pytest
from unittest.mock import patch
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.language import (
    nix_eval,
    nix_fmt,
    nix_lint,
    nix_repl_eval,
    nix_parse,
)


class TestNixEval:
    """Tests for nix_eval function."""

    @patch("tools.language._run_command")
    def test_eval_simple_expression(self, mock_run):
        """Test evaluating a simple expression."""
        mock_run.return_value = {
            "success": True,
            "stdout": "42",
            "stderr": "",
            "returncode": 0,
        }

        result = nix_eval("1 + 41")

        assert result["success"] is True
        assert result["result"] == 42

    @patch("tools.language._run_command")
    def test_eval_json_output(self, mock_run):
        """Test that JSON output is parsed."""
        mock_run.return_value = {
            "success": True,
            "stdout": json.dumps({"foo": "bar", "count": 5}),
            "stderr": "",
            "returncode": 0,
        }

        result = nix_eval('{ foo = "bar"; count = 5; }')

        assert result["success"] is True
        assert result["result"]["foo"] == "bar"
        assert result["result"]["count"] == 5

    @patch("tools.language._run_command")
    def test_eval_raw_output(self, mock_run):
        """Test raw string output."""
        mock_run.return_value = {
            "success": True,
            "stdout": "hello world",
            "stderr": "",
            "returncode": 0,
        }

        result = nix_eval('"hello world"', raw=True)

        assert result["success"] is True
        assert result["result"] == "hello world"

    @patch("tools.language._run_command")
    def test_eval_handles_error(self, mock_run):
        """Test error handling in eval."""
        mock_run.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "error: undefined variable 'foo'",
            "returncode": 1,
        }

        result = nix_eval("foo")

        assert result["success"] is False
        assert "error" in result


class TestNixFmt:
    """Tests for nix_fmt function."""

    @patch("tools.language._run_command")
    def test_fmt_success(self, mock_run):
        """Test successful formatting."""
        mock_run.return_value = {
            "success": True,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

        result = nix_fmt(".")

        assert result["success"] is True
        assert "formatted" in result["message"].lower()

    @patch("tools.language._run_command")
    def test_fmt_check_only(self, mock_run):
        """Test check-only mode."""
        mock_run.return_value = {
            "success": True,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

        result = nix_fmt(".", check_only=True)

        assert result["success"] is True
        assert "check" in result["message"].lower()

    @patch("tools.language._run_command")
    def test_fmt_check_fails(self, mock_run):
        """Test check mode failure."""
        mock_run.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "file needs formatting",
            "returncode": 1,
        }

        result = nix_fmt(".", check_only=True)

        assert result["success"] is False
        assert "need" in result["message"].lower()


class TestNixLint:
    """Tests for nix_lint function."""

    @patch("tools.language._run_command")
    def test_lint_no_issues(self, mock_run):
        """Test linting with no issues."""
        mock_run.return_value = {
            "success": True,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

        result = nix_lint(".")

        assert result["success"] is True

    @patch("tools.language._run_command")
    def test_lint_with_issues(self, mock_run):
        """Test linting with issues found."""
        mock_run.return_value = {
            "success": False,
            "stdout": "warning: unused variable 'x'",
            "stderr": "",
            "returncode": 1,
        }

        result = nix_lint(".")

        assert result["success"] is False
        assert "issues" in result


class TestNixParse:
    """Tests for nix_parse function."""

    @patch("tools.language._run_command")
    def test_parse_valid_file(self, mock_run):
        """Test parsing a valid file."""
        mock_run.return_value = {
            "success": True,
            "stdout": "# parsed AST output",
            "stderr": "",
            "returncode": 0,
        }

        result = nix_parse("test.nix")

        assert result["success"] is True
        assert "successfully" in result["message"]

    @patch("tools.language._run_command")
    def test_parse_invalid_file(self, mock_run):
        """Test parsing an invalid file."""
        mock_run.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "error: syntax error, unexpected '}', expecting ')'",
            "returncode": 1,
        }

        result = nix_parse("invalid.nix")

        assert result["success"] is False
        assert "error" in result
        assert "syntax" in result["error"].lower()


class TestNixReplEval:
    """Tests for nix_repl_eval function."""

    @patch("tools.language._run_command")
    def test_repl_eval_expression(self, mock_run):
        """Test evaluating in REPL context."""
        mock_run.return_value = {
            "success": True,
            "stdout": "Welcome to Nix 2.18\n\nnix-repl> 42\n\nnix-repl> ",
            "stderr": "",
            "returncode": 0,
        }

        result = nix_repl_eval("1 + 41")

        assert result["success"] is True
        # Result should be returned (filtering may vary)
        assert "result" in result

