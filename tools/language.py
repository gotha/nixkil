"""
Language & Analysis Tools

Tools for evaluating, formatting, linting, and analyzing Nix expressions.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


def _run_command(cmd: list[str], input_text: Optional[str] = None) -> dict:
    """Run a command and return structured result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            input=input_text,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def nix_eval(
    expression: str,
    raw: bool = False,
    json_output: bool = True,
) -> dict:
    """
    Evaluate a Nix expression.

    Args:
        expression: Nix expression to evaluate
        raw: If True, output raw string without quotes
        json_output: If True, output as JSON (default)

    Returns:
        Dict with evaluation result
    """
    cmd = ["nix", "eval", "--expr", expression]

    if raw:
        cmd.append("--raw")
    elif json_output:
        cmd.append("--json")

    result = _run_command(cmd)

    if result["success"]:
        output = result["stdout"].strip()
        if json_output and not raw:
            try:
                return {"success": True, "result": json.loads(output)}
            except json.JSONDecodeError:
                return {"success": True, "result": output}
        return {"success": True, "result": output}

    return {
        "success": False,
        "error": result.get("stderr", "Evaluation failed"),
    }


def nix_fmt(
    path: str = ".",
    check_only: bool = False,
) -> dict:
    """
    Format Nix files using the project's formatter.

    Args:
        path: Path to format (file or directory)
        check_only: If True, only check formatting without modifying

    Returns:
        Dict with formatting result
    """
    if check_only:
        cmd = ["nix", "fmt", "--", "--check", path]
    else:
        cmd = ["nix", "fmt", path]

    result = _run_command(cmd)

    if result["success"]:
        return {
            "success": True,
            "message": "Formatting check passed" if check_only else "Files formatted",
            "path": path,
        }

    if check_only:
        return {
            "success": False,
            "message": "Formatting check failed - files need formatting",
            "path": path,
            "details": result.get("stderr", ""),
        }

    return result


def nix_lint(path: str = ".") -> dict:
    """
    Lint Nix files for common issues.

    Uses statix if available, falls back to basic checks.

    Args:
        path: Path to lint (file or directory)

    Returns:
        Dict with linting results
    """
    # Try statix first (common Nix linter)
    cmd = ["statix", "check", path]
    result = _run_command(cmd)

    if result["returncode"] is not None:  # statix exists
        if result["success"]:
            return {
                "success": True,
                "message": "No linting issues found",
                "tool": "statix",
                "path": path,
            }
        return {
            "success": False,
            "message": "Linting issues found",
            "tool": "statix",
            "path": path,
            "issues": result["stdout"],
        }

    # Fallback: basic syntax check with nix-instantiate
    cmd = ["nix-instantiate", "--parse", path]
    result = _run_command(cmd)

    if result["success"]:
        return {
            "success": True,
            "message": "Syntax check passed (install statix for full linting)",
            "tool": "nix-instantiate",
            "path": path,
        }

    return {
        "success": False,
        "message": "Syntax error found",
        "tool": "nix-instantiate",
        "path": path,
        "error": result.get("stderr", ""),
    }


def nix_repl_eval(expression: str, flake_ref: Optional[str] = None) -> dict:
    """
    Evaluate expression in nix repl context.

    Args:
        expression: Expression to evaluate
        flake_ref: Optional flake to load (e.g., "nixpkgs")

    Returns:
        Dict with evaluation result
    """
    # Build repl input
    repl_input = expression + "\n:q\n"

    if flake_ref:
        cmd = ["nix", "repl", flake_ref]
    else:
        cmd = ["nix", "repl"]

    result = _run_command(cmd, input_text=repl_input)

    # Parse output (skip banner and prompts)
    output_lines = result["stdout"].split("\n")
    relevant_lines = [
        line for line in output_lines
        if not line.startswith("nix-repl>")
        and not line.startswith("Welcome")
        and line.strip()
    ]

    return {
        "success": True,
        "result": "\n".join(relevant_lines),
        "flake": flake_ref,
    }


def nix_parse(path: str) -> dict:
    """
    Parse a Nix file and check for syntax errors.

    Args:
        path: Path to Nix file

    Returns:
        Dict with parse result (success or error details)
    """
    cmd = ["nix-instantiate", "--parse", path]
    result = _run_command(cmd)

    if result["success"]:
        return {
            "success": True,
            "message": f"File '{path}' parsed successfully",
            "path": path,
        }

    # Extract error information
    stderr = result.get("stderr", "")
    return {
        "success": False,
        "message": "Parse error",
        "path": path,
        "error": stderr,
    }

