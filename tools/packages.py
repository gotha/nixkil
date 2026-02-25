"""
Package Management Tools

Tools for searching, inspecting, and running Nix packages.
"""

import json
import subprocess
from typing import Optional


def _run_command(cmd: list[str], capture_output: bool = True) -> dict:
    """Run a command and return structured result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=300,
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


def nix_search(
    query: str,
    flake: str = "nixpkgs",
    max_results: int = 20,
) -> dict:
    """
    Search for packages in nixpkgs or a flake.

    Args:
        query: Search term (package name or description)
        flake: Flake to search (default: nixpkgs)
        max_results: Maximum number of results to return

    Returns:
        Dict with search results including package names and descriptions
    """
    cmd = ["nix", "search", flake, query, "--json"]
    result = _run_command(cmd)

    if result["success"]:
        try:
            packages = json.loads(result["stdout"])
            # Limit results
            limited = dict(list(packages.items())[:max_results])
            return {
                "success": True,
                "packages": limited,
                "total_found": len(packages),
                "returned": len(limited),
            }
        except json.JSONDecodeError:
            return {"success": False, "error": "Failed to parse JSON output"}

    return result


def nix_package_info(package: str, flake: str = "nixpkgs") -> dict:
    """
    Get detailed information about a package.

    Args:
        package: Package name (e.g., "hello", "python311")
        flake: Flake containing the package (default: nixpkgs)

    Returns:
        Dict with package metadata (version, description, license, etc.)
    """
    # Get package metadata
    cmd = [
        "nix",
        "eval",
        f"{flake}#legacyPackages.x86_64-linux.{package}.meta",
        "--json",
    ]
    result = _run_command(cmd)

    if result["success"]:
        try:
            meta = json.loads(result["stdout"])
            return {"success": True, "package": package, "meta": meta}
        except json.JSONDecodeError:
            return {"success": False, "error": "Failed to parse package metadata"}

    # Try alternative path for packages
    cmd = ["nix", "eval", f"{flake}#{package}.meta", "--json"]
    result = _run_command(cmd)

    if result["success"]:
        try:
            meta = json.loads(result["stdout"])
            return {"success": True, "package": package, "meta": meta}
        except json.JSONDecodeError:
            pass

    return {"success": False, "error": f"Package '{package}' not found", "stderr": result.get("stderr", "")}


def nix_run(
    package: str,
    args: Optional[list[str]] = None,
    flake: str = "nixpkgs",
) -> dict:
    """
    Run a package without installing it.

    Args:
        package: Package to run (e.g., "hello", "cowsay")
        args: Arguments to pass to the program
        flake: Flake containing the package (default: nixpkgs)

    Returns:
        Dict with command output
    """
    cmd = ["nix", "run", f"{flake}#{package}", "--"]
    if args:
        cmd.extend(args)

    return _run_command(cmd)


def nix_shell(packages: list[str], command: Optional[str] = None) -> dict:
    """
    Create a temporary shell with specified packages.

    Args:
        packages: List of packages to include
        command: Optional command to run in the shell

    Returns:
        Dict with shell creation result or command output
    """
    cmd = ["nix", "shell"]
    for pkg in packages:
        if "#" in pkg:
            cmd.append(pkg)
        else:
            cmd.append(f"nixpkgs#{pkg}")

    if command:
        cmd.extend(["--command", "sh", "-c", command])

    return _run_command(cmd)


def nix_build(
    target: str,
    out_link: Optional[str] = None,
    no_link: bool = False,
) -> dict:
    """
    Build a Nix derivation.

    Args:
        target: Build target (flake output or path)
        out_link: Path for result symlink (default: ./result)
        no_link: If True, don't create result symlink

    Returns:
        Dict with build result and output path
    """
    cmd = ["nix", "build", target]

    if no_link:
        cmd.append("--no-link")
    elif out_link:
        cmd.extend(["--out-link", out_link])

    cmd.append("--print-out-paths")

    result = _run_command(cmd)

    if result["success"]:
        paths = result["stdout"].strip().split("\n")
        return {"success": True, "output_paths": paths}

    return result

