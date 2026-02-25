"""
Nixkil Agent Tools

A collection of tools for AI agents to interact with Nix, NixOS, and the Nix ecosystem.
"""

from .packages import (
    nix_search,
    nix_package_info,
    nix_run,
    nix_shell,
    nix_build,
)

from .flakes import (
    flake_init,
    flake_show,
    flake_check,
    flake_update,
    flake_lock_info,
)

from .nixos import (
    nixos_option_search,
    nixos_option_info,
    nixos_rebuild,
    nixos_generations,
)

from .language import (
    nix_eval,
    nix_fmt,
    nix_lint,
    nix_repl_eval,
    nix_parse,
)

__all__ = [
    # Package tools
    "nix_search",
    "nix_package_info",
    "nix_run",
    "nix_shell",
    "nix_build",
    # Flake tools
    "flake_init",
    "flake_show",
    "flake_check",
    "flake_update",
    "flake_lock_info",
    # NixOS tools
    "nixos_option_search",
    "nixos_option_info",
    "nixos_rebuild",
    "nixos_generations",
    # Language tools
    "nix_eval",
    "nix_fmt",
    "nix_lint",
    "nix_repl_eval",
    "nix_parse",
]

