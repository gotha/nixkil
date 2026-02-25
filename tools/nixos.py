"""
NixOS Tools

Tools for managing NixOS systems, options, and configurations.
"""

import json
import subprocess
from typing import Optional


def _run_command(cmd: list[str], sudo: bool = False) -> dict:
    """Run a command and return structured result."""
    if sudo:
        cmd = ["sudo"] + cmd

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # Longer timeout for NixOS operations
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


def nixos_option_search(query: str, max_results: int = 20) -> dict:
    """
    Search for NixOS options.

    Args:
        query: Search term for option names or descriptions
        max_results: Maximum number of results

    Returns:
        Dict with matching options
    """
    # Use nixos-option or nix eval to search
    cmd = [
        "nix",
        "eval",
        "--raw",
        f"nixpkgs#lib.attrNames (builtins.filter (x: builtins.match \".*{query}.*\" x != null) (builtins.attrNames (import <nixpkgs/nixos> {{}}).options))",
    ]

    # Alternative: use online search or local options.json
    # This is a simplified implementation
    result = _run_command(cmd)

    if not result["success"]:
        # Fallback: suggest using online documentation
        return {
            "success": True,
            "message": f"Search for '{query}' in NixOS options",
            "suggestion": f"Visit https://search.nixos.org/options?query={query}",
            "note": "For comprehensive option search, use the NixOS options search website",
        }

    return result


def nixos_option_info(option: str) -> dict:
    """
    Get detailed information about a NixOS option.

    Args:
        option: Full option path (e.g., "services.nginx.enable")

    Returns:
        Dict with option details (type, default, description, example)
    """
    # Try to get option info using nixos-option
    cmd = ["nixos-option", option]
    result = _run_command(cmd)

    if result["success"]:
        return {
            "success": True,
            "option": option,
            "info": result["stdout"],
        }

    # Fallback: provide link to documentation
    return {
        "success": True,
        "option": option,
        "documentation": f"https://search.nixos.org/options?query={option}",
        "note": "Use nixos-option command on a NixOS system for detailed info",
    }


def nixos_rebuild(
    action: str = "switch",
    flake: Optional[str] = None,
    hostname: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    """
    Rebuild NixOS configuration.

    Args:
        action: Rebuild action (switch, boot, test, build, dry-activate)
        flake: Flake reference (e.g., ".#myhost")
        hostname: Target hostname for flake-based builds
        dry_run: If True, only show what would be built

    Returns:
        Dict with rebuild result
    """
    valid_actions = ["switch", "boot", "test", "build", "dry-activate", "dry-build"]
    if action not in valid_actions:
        return {"success": False, "error": f"Invalid action. Must be one of: {valid_actions}"}

    cmd = ["nixos-rebuild", action]

    if flake:
        if hostname:
            cmd.extend(["--flake", f"{flake}#{hostname}"])
        else:
            cmd.extend(["--flake", flake])

    if dry_run or action.startswith("dry"):
        return {
            "success": True,
            "message": f"Would run: sudo {' '.join(cmd)}",
            "note": "Dry run - no changes made",
            "command": cmd,
        }

    # Actual rebuild requires sudo
    result = _run_command(cmd, sudo=True)

    if result["success"]:
        return {
            "success": True,
            "message": f"NixOS {action} completed successfully",
            "action": action,
        }

    return result


def nixos_generations(
    profile: str = "system",
    limit: int = 10,
) -> dict:
    """
    List NixOS generations.

    Args:
        profile: Profile to list (default: system)
        limit: Maximum number of generations to show

    Returns:
        Dict with generation information
    """
    if profile == "system":
        profile_path = "/nix/var/nix/profiles/system"
    else:
        profile_path = profile

    cmd = ["nix-env", "--list-generations", "--profile", profile_path]
    result = _run_command(cmd, sudo=True)

    if result["success"]:
        lines = result["stdout"].strip().split("\n")
        generations = []

        for line in lines[-limit:]:  # Get last N generations
            parts = line.split()
            if len(parts) >= 3:
                generations.append({
                    "id": parts[0],
                    "date": " ".join(parts[1:3]) if len(parts) > 2 else "",
                    "current": "(current)" in line,
                })

        return {
            "success": True,
            "profile": profile,
            "generations": generations,
            "total": len(lines),
        }

    return result

