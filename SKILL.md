---
name: nixkil
description: Agent skill for Nix language programming, Nix package manager, and NixOS
---

# nixkil

Agent skill for Nix language programming, Nix package manager, and NixOS.

## Tools

### Package Management
| Tool | Description |
|------|-------------|
| `nix_search` | Search for packages in nixpkgs |
| `nix_package_info` | Get detailed package metadata |
| `nix_run` | Run a package without installing |
| `nix_shell` | Enter a shell with packages available |
| `nix_build` | Build a package or derivation |

### Flake Operations
| Tool | Description |
|------|-------------|
| `flake_init` | Initialize a new flake project |
| `flake_show` | Show flake outputs |
| `flake_check` | Validate a flake |
| `flake_update` | Update flake inputs |
| `flake_lock_info` | Show lock file information |

### NixOS Configuration
| Tool | Description |
|------|-------------|
| `nixos_option_search` | Search NixOS options |
| `nixos_option_info` | Get option details and documentation |
| `nixos_rebuild` | Rebuild NixOS system configuration |
| `nixos_generations` | List system generations |

### Language Analysis
| Tool | Description |
|------|-------------|
| `nix_eval` | Evaluate Nix expressions |
| `nix_fmt` | Format Nix files |
| `nix_lint` | Lint Nix files for issues |
| `nix_repl_eval` | Evaluate in REPL context |
| `nix_parse` | Parse and validate Nix syntax |

## Knowledge Areas

| Area | Topics |
|------|--------|
| `nix-language` | Syntax, types, functions, builtins, derivations |
| `nixpkgs` | Package overrides, overlays, cross-compilation |
| `flakes` | Structure, inputs/outputs, commands, templates |
| `devenv` | Development environments with services and pre-commit hooks |
| `nixos` | System configuration, modules, services |
| `nix-darwin` | macOS configuration with Nix |
| `home-manager` | User environment and dotfiles management |
| `macos-linux-builder` | Building Linux packages on macOS |
| `troubleshooting` | Common errors and solutions |

## Examples

### DevShell Examples
- `examples/devshells/golang/` - Go development environment
- `examples/devshells/python/` - Python with venv and tooling
- `examples/devshells/rust/` - Rust with cargo tools
- `examples/devshells/nodejs/` - Node.js with TypeScript
- `examples/devshells/java/` - Java with Maven and Gradle
- `examples/devshells/multi-lang/` - Multiple languages in one flake

### Devenv Examples
- `examples/devenv/basic/` - Basic devenv setup
- `examples/devenv/with-services/` - PostgreSQL, Redis services
- `examples/devenv/with-precommit/` - Pre-commit hooks configuration

