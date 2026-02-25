"""
Flake Tools

Tools for initializing, inspecting, and managing Nix flakes.
"""

import json
import subprocess
from pathlib import Path
from typing import Optional


def _run_command(cmd: list[str], cwd: Optional[str] = None) -> dict:
    """Run a command and return structured result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=cwd,
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


def flake_init(
    path: str = ".",
    template: Optional[str] = None,
) -> dict:
    """
    Initialize a new flake in the specified directory.

    Args:
        path: Directory to initialize (default: current directory)
        template: Optional template to use (e.g., "templates#python")

    Returns:
        Dict with initialization result
    """
    cmd = ["nix", "flake", "init"]

    if template:
        cmd.extend(["--template", template])

    result = _run_command(cmd, cwd=path)

    if result["success"]:
        return {
            "success": True,
            "message": f"Flake initialized in {path}",
            "files_created": ["flake.nix"],
        }

    return result


def flake_show(flake_ref: str = ".") -> dict:
    """
    Show the outputs of a flake.

    Args:
        flake_ref: Flake reference (default: current directory)

    Returns:
        Dict with flake outputs structure
    """
    cmd = ["nix", "flake", "show", flake_ref, "--json"]
    result = _run_command(cmd)

    if result["success"]:
        try:
            outputs = json.loads(result["stdout"])
            return {"success": True, "flake": flake_ref, "outputs": outputs}
        except json.JSONDecodeError:
            # Return raw output if JSON parsing fails
            return {"success": True, "flake": flake_ref, "raw_output": result["stdout"]}

    return result


def flake_check(flake_ref: str = ".") -> dict:
    """
    Check a flake for errors.

    Args:
        flake_ref: Flake reference (default: current directory)

    Returns:
        Dict with check results (success/failure and any errors)
    """
    cmd = ["nix", "flake", "check", flake_ref]
    result = _run_command(cmd)

    if result["success"]:
        return {
            "success": True,
            "message": "Flake check passed",
            "flake": flake_ref,
        }

    return {
        "success": False,
        "message": "Flake check failed",
        "flake": flake_ref,
        "errors": result.get("stderr", ""),
    }


def flake_update(
    flake_ref: str = ".",
    inputs: Optional[list[str]] = None,
) -> dict:
    """
    Update flake lock file.

    Args:
        flake_ref: Flake reference (default: current directory)
        inputs: Specific inputs to update (default: all)

    Returns:
        Dict with update result
    """
    cmd = ["nix", "flake", "update"]

    if inputs:
        for input_name in inputs:
            cmd.append(input_name)

    cmd.append(flake_ref)

    result = _run_command(cmd)

    if result["success"]:
        return {
            "success": True,
            "message": "Flake inputs updated",
            "flake": flake_ref,
            "inputs_updated": inputs or "all",
        }

    return result


def flake_lock_info(flake_ref: str = ".") -> dict:
    """
    Get information about flake lock file.

    Args:
        flake_ref: Flake reference (default: current directory)

    Returns:
        Dict with lock file information (inputs, revisions, dates)
    """
    cmd = ["nix", "flake", "metadata", flake_ref, "--json"]
    result = _run_command(cmd)

    if result["success"]:
        try:
            metadata = json.loads(result["stdout"])
            locks = metadata.get("locks", {}).get("nodes", {})

            # Extract useful info from each input
            inputs_info = {}
            for name, info in locks.items():
                if name == "root":
                    continue
                locked = info.get("locked", {})
                inputs_info[name] = {
                    "type": locked.get("type"),
                    "owner": locked.get("owner"),
                    "repo": locked.get("repo"),
                    "rev": locked.get("rev", "")[:12] if locked.get("rev") else None,
                    "lastModified": locked.get("lastModified"),
                }

            return {
                "success": True,
                "flake": flake_ref,
                "description": metadata.get("description"),
                "inputs": inputs_info,
            }
        except json.JSONDecodeError:
            return {"success": False, "error": "Failed to parse metadata"}

    return result

